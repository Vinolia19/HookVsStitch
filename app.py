from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "hookvsstitch.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():

    conn = get_db_connection()

    projects = conn.execute("""
        SELECT
            p.project_id,
            p.project_name,
            u.name AS owner,
            p.category,
            p.difficulty,
            p.start_date,
            p.target_date,
            p.status
        FROM projects p
        JOIN users u
            ON p.user_id = u.user_id
        ORDER BY p.project_id
    """).fetchall()

    total_projects = conn.execute("""
        SELECT COUNT(*) AS count
        FROM projects
    """).fetchone()["count"]

    completed_projects = conn.execute("""
        SELECT COUNT(*) AS count
        FROM projects
        WHERE status = 'Completed'
    """).fetchone()["count"]

    active_projects = conn.execute("""
        SELECT COUNT(*) AS count
        FROM projects
        WHERE status = 'In Progress'
    """).fetchone()["count"]

    not_started_projects = conn.execute("""
        SELECT COUNT(*) AS count
        FROM projects
        WHERE status = 'Not Started'
    """).fetchone()["count"]

    users = conn.execute("""
        SELECT
            user_id,
            name,
            email,
            created_at
        FROM users
        ORDER BY name
    """).fetchall()

    stitches = conn.execute("""
        SELECT
            s.stitch_id,
            s.stitch_name,
            s.abbreviation,
            s.description,
            COALESCE(SUM(rs.quantity), 0) AS total_usage
        FROM stitches s
        LEFT JOIN row_stitches rs
            ON s.stitch_id = rs.stitch_id
        GROUP BY
            s.stitch_id,
            s.stitch_name,
            s.abbreviation,
            s.description
        ORDER BY total_usage DESC
    """).fetchall()

    materials = conn.execute("""
        SELECT
            p.project_name,
            m.material_name,
            m.material_type,
            pm.quantity,
            m.unit
        FROM projects p
        JOIN patterns pat
            ON p.project_id = pat.project_id
        JOIN pattern_materials pm
            ON pat.pattern_id = pm.pattern_id
        JOIN materials m
            ON pm.material_id = m.material_id
        ORDER BY
            p.project_name,
            m.material_name
    """).fetchall()

    try:

        progress_summary = conn.execute("""
            SELECT *
            FROM project_progress_summary
            ORDER BY completion_percentage DESC
        """).fetchall()

    except sqlite3.Error:

        progress_summary = conn.execute("""
            SELECT
                p.project_id,
                p.project_name,
                COUNT(pr.row_id) AS total_rows,
                COALESCE(
                    SUM(
                        CASE
                            WHEN prog.completed = 1 THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS completed_rows,
                CASE
                    WHEN COUNT(pr.row_id) = 0 THEN 0
                    ELSE ROUND(
                        100.0 *
                        SUM(
                            CASE
                                WHEN prog.completed = 1 THEN 1
                                ELSE 0
                            END
                        )
                        / COUNT(pr.row_id),
                        2
                    )
                END AS completion_percentage
            FROM projects p
            LEFT JOIN patterns pat
                ON p.project_id = pat.project_id
            LEFT JOIN pattern_rows pr
                ON pat.pattern_id = pr.pattern_id
            LEFT JOIN progress prog
                ON p.project_id = prog.project_id
                AND pr.row_id = prog.row_id
            GROUP BY
                p.project_id,
                p.project_name
            ORDER BY completion_percentage DESC
        """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        projects=projects,
        users=users,
        stitches=stitches,
        materials=materials,
        progress_summary=progress_summary,
        total_projects=total_projects,
        completed_projects=completed_projects,
        active_projects=active_projects,
        not_started_projects=not_started_projects
    )


@app.route("/project/<int:project_id>")
def project_details(project_id):

    conn = get_db_connection()

    project = conn.execute("""
        SELECT
            p.project_id,
            p.user_id,
            p.project_name,
            p.category,
            p.difficulty,
            p.start_date,
            p.target_date,
            p.status,
            u.name AS owner,
            u.email AS owner_email
        FROM projects p
        JOIN users u
            ON p.user_id = u.user_id
        WHERE p.project_id = ?
    """, (project_id,)).fetchone()

    if project is None:

        conn.close()

        return jsonify({
            "error": "Project not found"
        }), 404

    pattern = conn.execute("""
        SELECT
            pattern_id,
            project_id,
            pattern_name,
            description
        FROM patterns
        WHERE project_id = ?
        ORDER BY pattern_id
        LIMIT 1
    """, (project_id,)).fetchone()

    rows = conn.execute("""
        SELECT
            pr.row_id,
            pr.pattern_id,
            pr.row_number,
            pr.instruction,
            pr.expected_stitches
        FROM pattern_rows pr
        JOIN patterns pat
            ON pr.pattern_id = pat.pattern_id
        WHERE pat.project_id = ?
        ORDER BY pr.row_number
    """, (project_id,)).fetchall()

    row_stitches = conn.execute("""
        SELECT
            rs.row_stitch_id,
            rs.row_id,
            rs.stitch_id,
            rs.quantity,
            s.stitch_name,
            s.abbreviation,
            s.description
        FROM row_stitches rs
        JOIN stitches s
            ON rs.stitch_id = s.stitch_id
        JOIN pattern_rows pr
            ON rs.row_id = pr.row_id
        JOIN patterns pat
            ON pr.pattern_id = pat.pattern_id
        WHERE pat.project_id = ?
        ORDER BY
            pr.row_number,
            s.stitch_name
    """, (project_id,)).fetchall()

    materials = conn.execute("""
        SELECT
            m.material_id,
            m.material_name,
            m.material_type,
            m.unit,
            pm.quantity
        FROM patterns pat
        JOIN pattern_materials pm
            ON pat.pattern_id = pm.pattern_id
        JOIN materials m
            ON pm.material_id = m.material_id
        WHERE pat.project_id = ?
        ORDER BY m.material_name
    """, (project_id,)).fetchall()

    progress = conn.execute("""
        SELECT
            prog.progress_id,
            prog.project_id,
            prog.row_id,
            prog.completed,
            prog.completed_at,
            pr.row_number,
            pr.instruction,
            pr.expected_stitches
        FROM progress prog
        JOIN pattern_rows pr
            ON prog.row_id = pr.row_id
        WHERE prog.project_id = ?
        ORDER BY pr.row_number
    """, (project_id,)).fetchall()

    conn.close()

    return jsonify({
        "project": dict(project),
        "pattern": dict(pattern) if pattern else None,
        "rows": [dict(row) for row in rows],
        "row_stitches": [dict(row) for row in row_stitches],
        "materials": [dict(row) for row in materials],
        "progress": [dict(row) for row in progress]
    })


@app.route("/table/<table_name>")
def database_table(table_name):

    allowed_tables = {
        "users",
        "projects",
        "patterns",
        "pattern_rows",
        "stitches",
        "row_stitches",
        "materials",
        "pattern_materials",
        "progress"
    }

    if table_name not in allowed_tables:

        return jsonify({
            "error": "Invalid table"
        }), 400

    conn = get_db_connection()

    try:

        columns_info = conn.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()

        columns = [
            column["name"]
            for column in columns_info
        ]

        records = conn.execute(
            f"SELECT * FROM {table_name}"
        ).fetchall()

        return jsonify({
            "table": table_name,
            "columns": columns,
            "records": [dict(record) for record in records]
        })

    except sqlite3.Error as error:

        return jsonify({
            "error": str(error)
        }), 500

    finally:

        conn.close()


@app.route("/database-info")
def database_info():

    conn = get_db_connection()

    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    views = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'view'
        ORDER BY name
    """).fetchall()

    indexes = conn.execute("""
        SELECT
            name,
            tbl_name
        FROM sqlite_master
        WHERE type = 'index'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    conn.close()

    return jsonify({
        "tables": [dict(table) for table in tables],
        "views": [dict(view) for view in views],
        "indexes": [dict(index) for index in indexes]
    })


if __name__ == "__main__":

    print()
    print("==========================================")
    print("🧶 HookVsStitch Website")
    print("==========================================")
    print(f"Database: {DATABASE}")
    print("Website: http://127.0.0.1:5000")
    print("==========================================")
    print()

    app.run(
        debug=True,
        use_reloader=False
    )