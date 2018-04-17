from flask import Flask, render_template, request
import json
from VirtualJudgeSpider.config import Account
from VirtualJudgeSpider.control import Controller
from VirtualJudgeSpider.config import Problem, Result
import traceback
import time

app = Flask(__name__, template_folder='.')


@app.route("/submit", methods=['POST'])
def submit():
    try:
        source_code = request.files['source_code']
        if request.form.get('remote_oj') and request.form.get('language') and request.form.get(
                'remote_id') and source_code:
            remote_oj = request.form['remote_oj']
            remote_id = request.form['remote_id']
            language = request.form['language']

            ans = False
            tries = 3
            print('start')
            account = Account('robot4test', 'robot4test')
            while ans is False and tries > 0:
                tries -= 1
                controller = Controller(str(remote_oj))
                ans = controller.submit_code(pid=remote_id, account=account,
                                             code=source_code.read(), language=language)
                account.set_cookies(controller.get_cookies())
            if ans is False:
                return "SUBMIT FAILED"
            controller = Controller(remote_oj)
            result = controller.get_result(account=account, pid=remote_id)
            account.set_cookies(controller.get_cookies())
            print('end')
            tries = 5
            while result.status == Result.Status.STATUS_RESULT and tries > 0:
                time.sleep(2)
                if Controller(remote_oj).is_waiting_for_judge(result.verdict):
                    result = Controller(remote_oj).get_result_by_rid_and_pid(rid=result.origin_run_id,
                                                                             pid=remote_id)
                else:
                    break
                tries -= 1

            if result.status == Result.Status.STATUS_RESULT:
                return str(result.__dict__)
            return result.status.name
    except:
        traceback.print_exc()
    return "Error"


@app.route("/raw/<string:remote_oj>/<string:remote_id>")
def get_raw(remote_oj, remote_id):
    problem = Controller(remote_oj).get_problem(remote_id, account=Account('robot4test', 'robot4test'))
    if problem and problem.status:
        problem.status = problem.status.value
        return '<xmp>' + str(
            json.dumps(problem.__dict__, sort_keys=True, indent=4)) + '</xmp>'
    return 'No Such OJ'


@app.route("/languages/<string:remote_oj>")
def language(remote_oj):
    return json.dumps({
        'languages': Controller(remote_oj).find_language(account=Account('robot4test', 'robot4test'))
    })


@app.route("/<string:remote_oj>/<string:remote_id>")
def problem(remote_oj, remote_id):
    problem = Controller(remote_oj).get_problem(remote_id, account=Account('robot4test', 'robot4test'))
    if problem.status == Problem.Status.STATUS_CRAWLING_SUCCESS:
        return problem.html
    return problem.status.name


@app.route("/supports")
def supports():
    return json.dumps({
        'supports': Controller.get_supports()
    })


@app.route("/")
def index():
    return render_template('server.html')


if __name__ == '__main__':
    app.run(debug=True, port=7777, host='0.0.0.0')
