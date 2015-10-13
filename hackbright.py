"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect to database."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackbright.db'
    db.app = app
    db.init_app(app)


def get_student_by_github(github2):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM Students
        WHERE github = :github1
        """
    db_cursor = db.session.execute(QUERY, {'github1': github2})
    print "db_cursor: {}".format(db_cursor)
    print "type: {}".format(type(db_cursor))
    row = db_cursor.fetchone()
    print "row: {}".format(row)
    print "type: {}".format(type(row))
    print "Student: %s %s\nGithub account: %s" % (row[0], row[1], row[2])


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """
        INSERT INTO Students 
        VALUES (:first_name, :last_name, :github)
        """

    db_cursor = db.session.execute(QUERY, {'first_name': first_name, 
                               'last_name': last_name, 'github': github})
    db.session.commit()
    print "Successfully added student: %s %s" % (first_name, last_name)


def get_project_by_title(title):
    """Given a project title, print information about the project."""
    QUERY = """
        SELECT description, max_grade
        FROM Projects
        WHERE title = :title
    """
    db_cursor = db.session.execute(QUERY, {'title': title})
    row = db_cursor.fetchone()
    print "{}: {}. Max Grade: {}".format(title, row[0], row[1])


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""
    QUERY = """
        SELECT s.first_name, s.last_name, g.grade
        FROM Grades AS g
        JOIN Students AS s ON (g.student_github = s.github)
        WHERE g.student_github = :github AND g.project_title = :title
    """

    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title})

    row = db_cursor.fetchone()
    print row
    print "{} {} earned {} on {}!".format(row[0], row[1], row[2], title)


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""
    QUERY = """
    INSERT INTO Grades
    VALUES (:github, :title, :grade)
    """
    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title, 'grade': grade})
    db.session.commit()
    print "Successfully added {} as grade for {} for github account {}.".format(grade, title, github)


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args   # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "project_title": # FIXME if title is not in the database, errors out
            title = args[0]
            title = title.capitalize()
            get_project_by_title(title)

        elif command == "get_grade":
            github = args[0]
            title = args[1]
            title = title.capitalize()
            get_grade_by_github_title(github, title)

        elif command == "assign_grade":
            github, title, grade = args
            title = title.capitalize()
            grade = int(grade)
            github = github.lower()
            assign_grade(github, title, grade)

        else:
            if command != "quit":
                print "Invalid Entry. Try again."


if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    handle_input()

    # To be tidy, we'll close our database connection -- though, since this
    # is where our program ends, we'd quit anyway.

    db.session.close()
