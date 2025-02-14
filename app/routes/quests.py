import sqlite3

from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required

from app import app
from connection import get_db_connection


@app.get("/")
def get_start():
    if current_user.is_authenticated:
        if not current_user.email_verified:
            return redirect(url_for("get_verification"))
        return redirect(url_for("get_menu_page"))
    return redirect(url_for("get_login"))
    

@app.get("/menu/")
@login_required
def get_menu_page():
    if not current_user.email_verified:
        return redirect(url_for("get_verification"))
    
    conn = get_db_connection()
    quests = conn.execute("""
        SELECT q.*, CASE WHEN cq.quest_id IS NOT NULL THEN 1 ELSE 0 END as is_completed
        FROM quests q
        LEFT JOIN completed_quests cq ON q.quest_id = cq.quest_id 
        AND cq.user_id = ?""", 
        (current_user.user_id,)).fetchall()
    conn.close()
    
    if current_user.username == "admin":
        return render_template("admin_page.html", quests=quests)
    
    return render_template("menu.html", quests=quests)


@app.get("/add_quests/")
@login_required
def get_add_quests():
    conn = get_db_connection()
    quests = conn.execute("SELECT * FROM quests").fetchall()
    conn.close()
    return render_template("add_quests.html", quests=quests)


@app.post("/add_quests/")
@login_required
def post_add_quests():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    points = request.form.get("points", "").strip()
    answer = request.form.get("answer", "").strip()
    
    if not all([name, description, points, answer]):
        missing_fields = []
        if not name: missing_fields.append("name")
        if not description: missing_fields.append("description")
        if not points: missing_fields.append("points")
        if not answer: missing_fields.append("answer")
        return f"Missing required fields: {", ".join(missing_fields)}", 400
    
    if len(name) > 100:
        return "Quest name cannot exceed 100 characters", 400
    
    if len(description) > 1000:
        return "Quest description cannot exceed 1000 characters", 400
    
    try:
        points_int = int(points)
        if points_int <= 0 or points_int > 1000:
            return "Points must be between 1 and 1000", 400
    except ValueError:
        return "Points must be a valid number", 400
    
    try:
        conn = get_db_connection()
        existing_quest = conn.execute("SELECT quest_id FROM quests WHERE name = ?", (name,)).fetchone()
        if existing_quest:
            conn.close()
            return "A quest with this name already exists. Please choose a different name", 400
        
        conn.execute("INSERT INTO quests (name, description, points, answer) VALUES (?, ?, ?, ?)", 
                     (name, description, points_int, answer))
        conn.commit()
        conn.close()
        return redirect(url_for("get_add_quests"))
    except sqlite3.Error as e:
        error_message = str(e).lower()
        if "unique constraint" in error_message:
            if "name" in error_message:
                return "A quest with this name already exists", 400
            elif "description" in error_message:
                return "A quest with this description already exists", 400
        return "Database error occurred. Please try again", 500
    finally:
        if "conn" in locals():
            conn.close()


@app.get("/quest/<int:quest_id>")
@login_required
def get_quest(quest_id):
    conn = get_db_connection()
    quest = conn.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,)).fetchone()
    
    completed = conn.execute("""
        SELECT * FROM completed_quests 
        WHERE user_id = ? AND quest_id = ?""", 
        (current_user.user_id, quest_id)).fetchone()
    conn.close()
    
    if quest is None:
        return "Quest not found", 404
    
    if completed:
        return redirect(url_for("get_menu_page"))
        
    return render_template("completing_quests.html", quest=quest, completed=completed)


@app.post("/quest/<int:quest_id>/submit")
@login_required
def submit_quest(quest_id):
    user_answer = request.form.get("answer", "").strip()
    
    conn = get_db_connection()
    quest = conn.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,)).fetchone()
    
    if quest is None:
        conn.close()
        return "Quest not found", 404
    
    completed = conn.execute("""
        SELECT * FROM completed_quests 
        WHERE user_id = ? AND quest_id = ?""", 
        (current_user.user_id, quest_id)).fetchone()
    
    if completed:
        conn.close()
        return "Quest already completed", 400
    
    if user_answer == quest["answer"]:
        try:
            conn.execute("""
            INSERT INTO completed_quests (user_id, quest_id)
            VALUES (?, ?)""", 
            (current_user.user_id, quest_id))
            
            conn.execute("""
            UPDATE profile 
            SET points = points + ? 
            WHERE user_id = ? """, 
            (quest["points"], current_user.user_id))
            
            conn.commit()
            return "Correct! Points added to your profile.", 200
        except sqlite3.Error as e:
            conn.rollback()
            return "Database error occurred", 500
        finally:
            conn.close()
    else:
        conn.close()
        return "Incorrect answer, try again", 400


@app.get("/edit_quest/<int:quest_id>/form")
@login_required
def edit_quest_form(quest_id):
    if current_user.username != "admin":
        return redirect(url_for("get_menu_page"))
        
    conn = get_db_connection()
    quest = conn.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,)).fetchone()
    conn.close()
    
    if quest is None:
        return "Quest not found", 404
        
    return render_template("edit_quest.html", quest=quest)


@app.post("/edit_quest/<int:quest_id>")
@login_required
def edit_quest(quest_id):
    if current_user.username != "admin":
        return redirect(url_for("get_menu_page"))
        
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    points = request.form.get("points", "").strip()
    answer = request.form.get("answer", "").strip()
    
    if not all([name, description, points, answer]):
        flash("All fields are required", "error")
        return redirect(url_for("edit_quest_form", quest_id=quest_id))
    
    try:
        points_int = int(points)
        if points_int <= 0 or points_int > 1000:
            flash("Points must be between 1 and 1000", "error")
            return redirect(url_for("edit_quest_form", quest_id=quest_id))
    except ValueError:
        flash("Points must be a valid number", "error")
        return redirect(url_for("edit_quest_form", quest_id=quest_id))
    
    try:
        conn = get_db_connection()
        existing = conn.execute(
            "SELECT quest_id FROM quests WHERE name = ? AND quest_id != ?", 
            (name, quest_id)).fetchone()
        
        if existing:
            flash("A quest with this name already exists", "error")
            return redirect(url_for("edit_quest_form", quest_id=quest_id))
            
        conn.execute("""
            UPDATE quests 
            SET name = ?, description = ?, points = ?, answer = ? 
            WHERE quest_id = ?""", 
            (name, description, points_int, answer, quest_id))
        conn.commit()
        conn.close()
        flash("Quest updated successfully", "success")
        return redirect(url_for("get_menu_page"))
        
    except sqlite3.Error as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for("edit_quest_form", quest_id=quest_id))


@app.post("/delete_quest/<int:quest_id>")
@login_required
def delete_quest(quest_id):
    if current_user.username != "admin":
        return redirect(url_for("get_menu_page"))
        
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM completed_quests WHERE quest_id = ?", (quest_id,))
        conn.execute("DELETE FROM quests WHERE quest_id = ?", (quest_id,))
        conn.commit()
        conn.close()
        flash("Quest deleted successfully", "success")
        return redirect(url_for("get_menu_page"))
        
    except sqlite3.Error as e:
        flash(f"Error deleting quest: {str(e)}", "error")
        return redirect(url_for("get_menu_page"))
