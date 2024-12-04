import subprocess

def all_remove():
    try:
        subprocess.run([
            'kubectl', 'exec', '-n', 'after-migration', 'deploy/after-wordpress',
            '--', 'rm', '-rf', '/var/www/html/'
        ], check=True,text=True,
            capture_output=True)
    except subprocess.CalledProcessError as error:
        raise Exception(f"Error all_remove: {error}")
    
# all_remove()