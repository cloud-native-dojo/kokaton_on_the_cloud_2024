import subprocess

# 最優先で送るファイル
pri_items = [
    "wp-content",
    "wp-includes",
]

# wpの最優先ファイル転送 (rsync)
def pri_rsync_wp_files():
    try:
        for pri_item in pri_items:
            subprocess.run([
                'kubectl', 'exec', '-n', 'before-migration', 'deploy/before-wordpress', '--',
                'sshpass', '-p', 'dojo', 'rsync', '-e', 'ssh -p 22 -o StrictHostKeyChecking=no', '-avz',
                f'/var/www/html/{pri_item}', 'dojo@after-wordpress.after-migration:/var/www/html'
            ], check=True)

    except subprocess.CalledProcessError as error:
        raise Exception(f"Error pri_rsync_wp_files: {error}")
    
pri_rsync_wp_files()
