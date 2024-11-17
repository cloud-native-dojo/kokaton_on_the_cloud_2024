import subprocess

# DBをダンプ、Podに転送
def dump_wp_db():
    sql_file_path = "/tmp/wp_db.sql"
    db_user = "before-wordpress-user"
    db_password = "before-wordpress-2024"
    db_name = "before-wordpress-db"

    try:
        dump_process = subprocess.Popen([
            "kubectl", "exec", "-n", "before-migration",
            "deploy/before-wordpress-sql", "--", "sh", "-c",
            f"mysqldump -u {db_user} -p{db_password} --no-tablespaces --single-transaction {db_name}"],
            stdout=subprocess.PIPE)
        transfer_process = subprocess.Popen([
            "kubectl", "exec", "-i", "-n", "after-migration",
            "deploy/after-wordpress-sql", "--", "sh", "-c",
            f"cat > {sql_file_path}"],
            stdin=dump_process.stdout)

        dump_process.stdout.close()
        transfer_process.communicate()

    except subprocess.CalledProcessError as error:
        raise Exception(f"Error dump_wp_db: {error}")


# DBをリストア     
def restore_wp_db():
    sql_file_path = "/tmp/wp_db.sql"
    db_user = "after-wordpress-user"
    db_password = "after-wordpress-2024"
    db_name = "after-wordpress-db"

    try:
        subprocess.run([
            "kubectl", "exec", "-i", "-n", "after-migration",
            "deploy/after-wordpress-sql", "--", "sh", "-c",
            f"mysql -u {db_user} -p{db_password} {db_name} < {sql_file_path}"],
            check=True)

    except subprocess.CalledProcessError as error:
        raise Exception(f"Error executing restore_wp_db: {error}")
