import subprocess


# var/www/htmlのバックアップ
def backup_wp_files():
    try:
        subprocess.run([
            'kubectl', 'exec', '-i', '-n', 'before-migration',
            'deploy/before-wordpress',
            '--', 'cp', '-r', '/var/www/html', '/tmp/wp_backup'
        ], check=True)

    except subprocess.CalledProcessError as error:
        raise Exception(f"Error backup_wp_files: {error}")


# wpのファイル転送 (rsync)
def rsync_wp_files():
    try:
        subprocess.run([
            'kubectl', 'exec', '-n', 'before-migration', 'deploy/before-wordpress', '--',
            'sshpass', '-p', 'dojo', 'rsync', '-e', 'ssh -p 22 -o StrictHostKeyChecking=no', '-avz',
            '/var/www/html/', 'dojo@after-wordpress.after-migration:/var/www/html'
        ], check=True)

    except subprocess.CalledProcessError as error:
        raise Exception(f"Error rsync_wp_files: {error}")
