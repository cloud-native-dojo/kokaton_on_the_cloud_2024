def all_remove():
    import subprocess
    try:
        subprocess.run([
            'kubectl', 'exec', '-n', 'after-migration', 'deploy/after-wordpress',
            '--', 'rm', '-rf', '/var/www/html/'
        ], check=True,text=True,
            capture_output=True)
    except subprocess.CalledProcessError as error:
        raise Exception(f"Error all_remove: {error}")

if __name__ == "__main__":
    all_remove()