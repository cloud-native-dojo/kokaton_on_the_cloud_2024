import subprocess

# 優先度に応じてファイルを転送する関数
def rsync_wp_files(chunk):
    for column, files in chunk.items():
        for file_path in files:
            try:
                subprocess.run([
                    'kubectl', 'exec', '-n', 'before-migration', 'deploy/before-wordpress', '--',
                    'sshpass', '-p', 'dojo', 'rsync', '-e', 'ssh -p 22 -o StrictHostKeyChecking=no', '-avz',
                    file_path, f'dojo@after-wordpress.after-migration:{file_path}',
                    '--rsync-path', f"mkdir -p $(dirname {file_path}) && rsync"
                ], check=True)
            except subprocess.CalledProcessError as error:
                print(f"Error sending file {file_path}: {error}")
