import os


from flask import Flask, escape, request, jsonify
from flaskext.mysql import MySQL
mysql = MySQL()

app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_DATABASE_PORT'] = int(os.environ.get('MYSQL_PORT'))
app.config['MYSQL_DATABASE_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('MYSQL_ROOT_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = 'hfrc_data'
mysql.init_app(app)


def run_query(formatted_query):
    """Convenience method to run a query"""
    cursor = mysql.get_db().cursor()
    cursor.execute(formatted_query)
    return jsonify(cursor.fetchall())


@app.route('/api/v1/user/all')
def userdata():
    query = f"""
    Select * 
    from user 
    where selcal_number = {request.args.get('selcal')}
    """
    return run_query(query)


@app.route('/api/v1/position/latest')
def latest_position():
    query = f"""
    select pos.* 
    from positions pos 
    where pos.pos_id = (SELECT max(pos2.pos_id) 
                        from positions pos2 
                        where pos2.user_id = (select u.user_id 
                                              from user u 
                                              where u.selcal_number = '{request.args.get('selcal')}'
                                              )
                        )
    """
    return run_query(query)


