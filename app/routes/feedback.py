from flask import render_template, redirect, url_for

from app import app
from app.forms import FeedbackForm
from connection import get_db_connection


@app.get("/feedback/")
def feedback_page():
    form = FeedbackForm()
    form.rating.choices = [(1, 'Negative'), (2, 'Positive')]
    connection = get_db_connection()
    feedbacks = connection.execute(
        "SELECT * FROM feedback").fetchall()
    connection.close()
    
    return render_template("feedback_page.html", form=form, feedbacks=feedbacks)


@app.post("/feedback/")
def add_feedback():
    form = FeedbackForm()
    form.rating.choices = [(1, 'Negative'), (2, 'Positive')]
    connection = get_db_connection()
    connection.execute(
        "INSERT INTO feedback (text, rating) VALUES (?, ?)",
        (form.text.data, form.rating.data))
    connection.commit()
    connection.close()
    
    return redirect(url_for('feedback_page'))
