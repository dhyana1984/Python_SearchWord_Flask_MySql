from flask import Flask, render_template, request,session, copy_current_request_context
from vsearch import search4letters
from DBcm import UseDataBase,ConnectionErrors,CredentialsError,SQLError
from checker import check_logged_in
from time import sleep
from threading import Thread

app = Flask(__name__)
app.secret_key = 'YouWillNeverGuessMySecretKey'

app.config['dbconfig'] =  { 'host':'127.0.0.1',
                            'user':'vsearch',
                            'password':'vsearchpasswd',
                            'database':'vsearchlogDB',}


#def log_request(req:'flask_request',res: str) -> None:
#    """log details of the web request and the results"""
#    dbconfig = app.config['dbconfig']
#    sleep(15)
#    with UseDataBase(dbconfig) as cursor: 
#        _SQL = """insert into log
#          (phrase, letters, ip, browser_string, results)
#          values
#          (%s,%s,%s,%s,%s)"""
#        cursor.execute(_SQL,(req.form['phrase'],
#                        req.form['letters'],
#                        req.remote_addr,
#                         req.user_agent.browser,
#                         res,))

       
     


@app.route('/search4', methods=['POST'])
def do_search() ->  'html' :
    
    @copy_current_request_context
    def log_request(req:'flask_request',res: str) -> None:
        #log details of the web request and the results
        dbconfig = app.config['dbconfig']
        sleep(15)
        with UseDataBase(dbconfig) as cursor: 
            _SQL = """insert into log
                    (phrase, letters, ip, browser_string, results)
                    values
                    (%s,%s,%s,%s,%s)"""
            cursor.execute(_SQL,(req.form['phrase'],
                         req.form['letters'],
                         req.remote_addr,
                         req.user_agent.browser,
                         res,))
    phrase = request.form['phrase']
    letters = request.form['letters']
    result = str(search4letters(phrase,letters))
    title = 'Here are your results:'
    try:
         t = Thread(target = log_request, args=(request,result))
         t.start()
    except Exception as err:
         print('****Logging failed with this error', str(err))
    return render_template('results.html',
                                                the_title = title,
                                                the_phrase = phrase,
                                                the_letters = letters,
                                                the_results = result)
@app.route('/')
@app.route('/entry')
def entry_page() -> 'html' :
     return render_template('entry.html',
                             the_title='Welcome to search4letters on the web!')

@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'Html':
    dbconfig = app.config['dbconfig'] 
    try:
        with UseDataBase(dbconfig) as cursor:
            _SQL = """ SELECT phrase, letters, ip, browser_string, results, ts FROM log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
            titles=('Phrase','Letters','User IP','User Browser','Results','CreateTime')
            return render_template('viewlog.html',
                           the_title ='View Log',
                           the_row_titles=titles,
                           the_data = contents)
    except ConnectionErrors as err:
        print('Is your db switched on? Error:',err)
    except CredentialsError as err:
        print('User-id/Password issues Error:',err)
    except SQLError as err:
        print('Is your query correct? Error:',err)
    except Exception as err:
        print('****Logging failed with this error', str(err))     

        
        
@app.route('/login')
def do_login() -> str:
    session["log_in"]= True
    return 'You are now logged in.'

@app.route('/logout')
def do_logout() -> str:
    session.pop('log_in')
    return 'You are now logged out!'

if __name__ =="__main__":
     app.run(debug=True)
