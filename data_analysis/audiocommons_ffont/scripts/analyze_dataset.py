# Need this to import from parent directory when running outside pycharm
import os
import glob
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from ac_utils.general import load_from_json, save_to_json, promt_user_to_abort_if_file_exists, print_progress, \
    seconds_to_day_hour_minute_second
from ac_utils.worker import WorkParallelizer
import tempo_estimation.analysis_algorithms as rhythm_algorithms
import key_estimation.analysis_algorithms as tonal_algorithms
import pitch_estimation.analysis_algorithms as pitch_algorithms
from ac_utils import analysis_algorithms as general_algorithms
celery_available = True
try:
    from tasks import run_analysis_algorithm
except ImportError:
    # This can happen if celery is not available and run_analysis_algorithm is not defined
    # We set the celery available flag here so the script knows
    celery_available = False
import click
import time


@click.command()
@click.argument('dataset_path')
@click.option('--algorithms', default='',
              help='Algorithm names separated by commas')
@click.option('--max_sounds', default=None, help='Max number of sounds to analyze (default None).')
@click.option('--save_every', default=100, help='Save analysis results every X processed sounds (default 100).')
@click.option('--incremental', default=False, is_flag=True,
              help='If an analysis file is found for the given algorithm and this option is set to true, the algorithm '
                   'will only analyse the sounds that have not been analysed yet (default False).')
@click.option('--use_celery', default=False, is_flag=True,
              help='Whether to use celery for running the analysis tasks (default False).')
@click.option('--force', default=False, is_flag=True,
              help='Overwrite existing analysis files without asking (default False).')
@click.option('--workers', default=4, help='Number of workers to use for parallelized analysis of audio files (default 4).')
def analyze_dataset(dataset_path, algorithms, max_sounds, save_every, incremental, use_celery, force, workers):
    """
    Analyze the audio files in a dataset with the specified algorithms.
    """
    
    if use_celery and not celery_available:
        print('Celery not found, will analyze ignoring --use_celery option')
        use_celery = False

    available_algorithms = list()
    for algorithms_set in [rhythm_algorithms, general_algorithms, tonal_algorithms, pitch_algorithms]:
        for item in dir(algorithms_set):
            if item.startswith('algorithm_'):
                available_algorithms.append([
                    item.replace('algorithm_', ''),
                    algorithms_set.__getattribute__(item)
                ])

    analysis_algorithms_to_run = list()
    algorithm_names = algorithms.split(',')
    for algorithm_name, algorithm_function in available_algorithms:
        if algorithm_name in algorithm_names:
            out_file_path = os.path.join(dataset_path, "analysis_%s.json" % algorithm_name)
            if not incremental and not force:
                if promt_user_to_abort_if_file_exists(out_file_path, throw_exception=False):
                    analysis_algorithms_to_run.append([algorithm_name, algorithm_function])
            else:
                analysis_algorithms_to_run.append([algorithm_name, algorithm_function])
    if not analysis_algorithms_to_run:
        click.echo('No analysis algorithms to run. Available algorithms are:')
        for name, _ in available_algorithms:
            click.echo('\t%s' % name)
        return

    if use_celery:
        click.echo('We detected you\'re using celery to run the tasks, here are some useful commands:')
        click.echo('\tsudo rabbitmq-server -detached             (start rabbitmq broker)')
        click.echo('\tsudo rabbitmqctl stop                      (stop rabbitmq broker)')
        click.echo('\tcelery -A tasks worker --concurrency=4     (start Celery workers)')
        click.echo('\tcelery -A tasks purge                      (clear Celery queue)')

    metadata = load_from_json(os.path.join(dataset_path, "metadata.json"))
    algorithms_run = 0
    for analysis_algorithm_name, analysis_algorithm in analysis_algorithms_to_run:
        start_timestamp = time.time()
        algorithms_run += 1
        click.echo("Analyzing '%s' dataset [%i/%i] - %s" %
                   (dataset_path, algorithms_run, len(analysis_algorithms_to_run), analysis_algorithm_name))
        if max_sounds is None:
            max_sounds = len(metadata)
        else:
            max_sounds = int(max_sounds)

        out_file_path = os.path.join(dataset_path, "analysis_%s.json" % analysis_algorithm_name)
        analysis_results = dict()
        if incremental and os.path.exists(out_file_path):
            # Load existing analysis file (if it exists)
            analysis_results = load_from_json(out_file_path)
            click.echo("Continuing existing analysis (%i sounds already analysed)" % len(analysis_results))

        label = "Sending sounds to analyze..."
        asynchronous_job_objects = None
        wp = None
        if use_celery:
            asynchronous_job_objects = list()
        else:
            wp = WorkParallelizer(show_widgets=False)
        with click.progressbar(list(metadata.values())[:max_sounds], label=label) as sounds_metadata:
            for count, sound in enumerate(sounds_metadata):
                if incremental:
                    if str(sound['id']) in analysis_results:
                        # If analysis for that sound already exists, continue iteration with the next sound
                        continue

                # If there is no existing analysis, run it
                try:
                    sound['file_path'] = glob.glob(dataset_path + '/audio/wav/' + str(sound['id']) + '_*.wav')[0]
                    if not use_celery:
                        # Add jobs to work paralellizer
                        wp.add_task(analysis_algorithm, sound, task_id=sound['id'])
                    else:
                        task_object = run_analysis_algorithm.delay(analysis_algorithm, sound)
                        asynchronous_job_objects.append((sound['id'], task_object))
                except Exception:
                    print("Could not find " + str(sound['id']))

        if use_celery and len(asynchronous_job_objects):
            # Enter a loop to check status of jobs and add jobs to metadata as they get done
            finished_asynchronous_job_objects = dict()
            n_total_jobs = len(asynchronous_job_objects)
            n_jobs_done_in_last_save = 0
            while len(asynchronous_job_objects) != 0:
                time.sleep(1)
                i = 0
                jobs_to_delete_from_list = list()  # store position of job_objects in asynchronous_job_objects
                # that will be deleted after each while iteration
                for sound_id, job_object in asynchronous_job_objects:
                    max_objects_to_check = 100
                    if job_object.ready():
                        # Job is finished
                        finished_asynchronous_job_objects[sound_id] = job_object
                        jobs_to_delete_from_list.append(i)
                        try:
                            analysis = job_object.get()
                            if analysis:
                                analysis_results[sound_id] = analysis
                            else:
                                continue
                        except RuntimeError:
                            pass
                    i += 1
                    if i >= max_objects_to_check:
                        # We only check the first 'max_objects_to_check' in each iteration.
                        # Assuming that jobs are being processed approximately in the order they were sent,
                        # we should be fine.
                        break
                for index in sorted(jobs_to_delete_from_list, reverse=True):
                    del asynchronous_job_objects[index]
                print_progress('Analyzing sounds...', len(finished_asynchronous_job_objects), n_total_jobs,
                               start_time=start_timestamp, show_progress_bar=True)
                # Estimate time remaining
                if len(finished_asynchronous_job_objects) - n_jobs_done_in_last_save >= save_every:
                    # Save progress every 100 analysed sounds
                    n_jobs_done_in_last_save += len(finished_asynchronous_job_objects)
                    save_to_json(out_file_path, analysis_results)
            print('')
        else:
            wp.start(num_workers=workers)
            while True:
                time.sleep(1)
                finished = wp.show_progress()
                
                tasks_succeeded = wp.tasks_succeeded()
                for task in tasks_succeeded:
                    sound_id = task.id
                    if sound_id not in analysis_results:
                        analysis_results[sound_id] = task.result(timeout=0.0)
                
                if len(tasks_succeeded) % save_every == 0:
                    save_to_json(out_file_path, analysis_results)
                
                if finished:
                    break
            
            wp.show_errors()
            
        # Report number of correctly analyzed sounds
        end_timestamp = time.time()
        click.echo('Analyzed dataset with %i sounds (%i sounds correctly analysed), done in %s'
                   % (len(metadata), len(analysis_results),
                      seconds_to_day_hour_minute_second(end_timestamp - start_timestamp)))
        save_to_json(out_file_path, analysis_results, verbose=True)
        
        
if __name__ == '__main__':
    analyze_dataset()
