import argparse
import yaml
import jinja2
import jinja2.meta
import os
import subprocess
import shutil
import stat

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the template configuration file")
    parser.add_argument("--mosaic_config", required=True, help="Path to the mosaic configuration file")
    parser.add_argument("--name", required=True, help="Name of the job")
    parser.add_argument("--sbatchj2", default="mosaic.sh.jinja", help="Name of the sbatch template file")
    parser.add_argument("--containerj2", default="container.sh.jinja", help="Name of the in-container template file")
    parser.add_argument("--template_dir", default="templates", help="Path to the directory containing Jinja2 templates")
    parser.add_argument("--run_dir", default="runs", help="Path to the directory where the ")
    parser.add_argument("--template", required=False, nargs=argparse.REMAINDER, help="Overwrite template variables in the format 'key=value'")
    return parser.parse_args()

def read_config(config_file):
    with open(config_file, "r") as f:
        return yaml.safe_load(f)

def update_config_with_args(config, args):
    config["job_name"] = args.name # explicitly add name
    for key, value in vars(args).items():
        if key == "template" and value:
            for arg in value:
                k, v = arg.split("=", 1)
                config[k] = v
        elif value:
            pass # can handle non-template arguments here
    return config

def get_template_variables(template_dir, template_names):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    variables = set()
    for template_name in template_names:
        template_source = env.loader.get_source(env, template_name)[0]
        parsed_content = env.parse(template_source)
        variables.update(jinja2.meta.find_undeclared_variables(parsed_content))
    return variables

def validate_config(config, template_variables):
    missing_variables = template_variables - set(config.keys())
    if missing_variables:
        raise ValueError(f"Missing configuration variables: {', '.join(missing_variables)}")

def render_template(env, template_name, output_path, config):
    template = env.get_template(template_name)
    with open(output_path, "w") as f:
        f.write(template.render(config).strip())

def submit_job(job_dir):
    cmd = ["sbatch", "sbatch.sh"]
    subprocess.run(cmd, cwd=job_dir, check=True)

def main():
    args = parse_arguments()
    config = read_config(args.config)
    config = update_config_with_args(config, args)

    template_dir = "templates"
    template_variables = get_template_variables(template_dir, [args.sbatchj2, args.containerj2])
    validate_config(config, template_variables)

    job_dir = os.path.join(args.run_dir, args.name)
    os.mkdir(job_dir) # fails if directory already exists
    os.mkdir(os.path.join(job_dir, "logs"))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    render_template(env, args.sbatchj2, os.path.join(job_dir, "sbatch.sh"), config)
    render_template(env, args.containerj2, os.path.join(job_dir, "container.sh"), config)
    os.chmod(os.path.join(job_dir, "sbatch.sh"), stat.S_IRWXU) # make the scripts executable
    os.chmod(os.path.join(job_dir, "container.sh"), stat.S_IRWXU)
    with open(os.path.join(job_dir, "config.yaml"), "w") as f: # save the configuration
        yaml.dump(config, f)
    shutil.copy2(args.mosaic_config, os.path.join(job_dir, "mosaic_config.yaml")) # copy the mosaic config (TODO: can we make this more general?)

    print(f"Job files generated in: {job_dir}")
    print(f"Configuration:\n{yaml.dump(config)}")
    confirm = input("Do you want to submit the job to Slurm? (y/N): ")
    if confirm.lower() == "y":
        submit_job(job_dir)
    else:
        print("Job submission canceled, remember to clean up manually.")

if __name__ == "__main__":
    main()