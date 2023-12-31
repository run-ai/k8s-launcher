import argparse
import os
import sys
import shutil

from subprocess import Popen

def replace_placeholders(file_path, output_file_path, replacement_dict):
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Replace placeholders with their corresponding values
    for placeholder, value in replacement_dict.items():
        content = content.replace(placeholder, str(value))

    # Write the modified content back to the file
    with open(output_file_path, 'w') as file:
        file.write(content)

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Replace placeholders in a YAML file.')
    parser.add_argument('--model', type=str, help='Size of model [126m, 5b]')
    parser.add_argument('--num_workers', type=int, help='Number of workers')
    parser.add_argument('--num_gpus', type=int, help='Number of GPUs per node')
    parser.add_argument('--results_dir', type=str, help='Directory to put the results', required=True)
    parser.add_argument('--data_dir', type=str, help='Path to where the preprocessed data exists', required=True)
    parser.add_argument('--image_pull_secret', type=str, help='Kubernetes secret that holds nvcr.io credentials')

    # Parse the arguments
    args = parser.parse_args()
    
    kubeflow_pytorch = args.num_workers is not None
    if kubeflow_pytorch:
        args.num_gpus = 1
    else:
        args.num_workers = 1
    # Build a dictionary of placeholders and their corresponding values
    replacements = {}
    model = "5b"
    if args.model is not None:
        model = args.model
    if args.num_workers is not None:
        replacements['<NUM_WORKERS>'] = args.num_workers
        replacements['<NUM_WORKERS_WITHOUT_MASTER>'] = args.num_workers - 1
    if args.num_gpus is not None:
        replacements['<NUM_GPUS>'] = args.num_gpus
    if args.results_dir is not None:
        replacements['<RESULTS_DIR>'] = args.results_dir
    if args.data_dir is not None:
        replacements['<DATA_DIR>'] = args.data_dir
    if args.image_pull_secret is not None:
        replacements['<NVCR.IO SECRET>'] = args.image_pull_secret


    if not os.path.exists('results'):
        os.makedirs('results')
    # Call the function with the provided arguments
    replace_placeholders(model + '/config.template', 'results/config.yaml', replacements)

    if kubeflow_pytorch:
        replace_placeholders(model + '/kubeflow-pytorch-job.yaml', 'results/kubeflow-pytorch-job.yaml', replacements)
    else:
        replace_placeholders(model + '/batch-job.yaml', 'results/batch-job.yaml', replacements)
    