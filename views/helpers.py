from flask import Blueprint, redirect, url_for, session, render_template, flash, request, jsonify
from flask_login import login_required
from models import get_db_connection
from context_processors import get_table_owner_status
from flask_mail import Mail

helpers_bp = Blueprint('helpers_bp', __name__)

# Helper for Mail logic
mail = Mail()


@helpers_bp.route('/clear_db', methods=['POST'])
@login_required
def clear_db():
    user_id = session.get('user_id') 
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks;")
    cursor.execute("DELETE FROM rooms;")
    cursor.execute("DELETE FROM flatmates;")

    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='tasks'")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='rooms'")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='flatmates'")
    cursor.execute("UPDATE users SET default_database=? WHERE user_id=?", (0, user_id))
    conn.commit()
    conn.close()

    flash('Database cleared successfully :( ', 'success')
    return redirect(url_for('main'))




@helpers_bp.route('/viewdata')
@login_required
def viewdata():

    user_id = session.get('user_id') 
    is_table_owner = get_table_owner_status()


    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC ;").fetchall()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY id DESC ;").fetchall()
    flatmates = conn.execute("SELECT * FROM flatmates ORDER BY id DESC ").fetchall()
    return render_template('viewdata.html', rooms=rooms, tasks=tasks, flatmates=flatmates)

@helpers_bp.route('/delete', methods=['POST'])
@login_required
def delete_entry():
    table_name = request.form.get('table_name')
    id_to_delete = int(request.form.get('id'))  # Cast to int
    conn = get_db_connection()

    # Safeguard against SQL Injection for table_name
    if table_name not in ['tasks', 'flatmates', 'rooms']:
        flash("Invalid table name", "danger")
        return redirect(url_for("main"))

    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (id_to_delete,))
    conn.commit()
    conn.close()

    if cursor.rowcount:
        flash("Entry successfully deleted", "success")
    else:
        flash("No such entry", "warning")
  
    return_url = request.referrer or url_for("main")
    return redirect(return_url)

@helpers_bp.route('/mark_complete', methods=['POST'])
@login_required
def mark_complete():
    try:
        task_id = int(request.form.get('task_id'))  # Cast to int
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE task_table SET task_complete = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        if cursor.rowcount:
            flash(f"Task {task_id} successfully marked as complete", "success")
        else:
            flash("No such task", "warning")
    except Exception as e:
        print("An error occurred:", str(e))
        flash("An error occurred while marking the task as complete", "error")

    return redirect(request.referrer or url_for("dashboard"))

@helpers_bp.route('/become_house_master', methods=["GET", 'POST'])
@login_required
def become_house_master():
    user_id = session.get('user_id')   

    # Establish a database connection and cursor
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the table_owner value to 1
    cursor.execute("UPDATE users SET table_owner = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('additems_bp.add_items'))

@helpers_bp.route('/become_house_member', methods=["GET", 'POST'])
@login_required
def become_house_member():
    
    # set table owner value to 0
    return redirect(url_for('dashboard_bp.dashboard'))
