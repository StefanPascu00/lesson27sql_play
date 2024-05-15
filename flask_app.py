from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.datastructures import auth

# from werkzeug.datastructures import auth
import company_func

config = company_func.initialise_config()
app = Flask(__name__)
users = {
    "user1": "parola1",
    "user2": "parola3"
}
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username: str, password: str):
    if username in users.keys():
        if password == users[username]:
            return True

    return False


@app.route("/")
def first_func():
    return {"message": "Hello world!"}


@app.route("/home", methods=['PUT', 'POST'])
def second_func():
    print(request.method)
    data = request.data
    data = data.decode()
    print(data)
    return {"message": "POST or PUT request"}


@app.route("/emps/<emp_id>", methods=["DELETE"])
@auth.login_required
def fire_employee(emp_id):
    if emp_id:
        sql_query = f"DELETE from company.employess where emp_id = {emp_id}"
        response = company_func.read_from_database(sql_query, config)
        if "DELETE 0" == response:
            return {"ERROR": "Employee not in database !"}
        return {"message": "Succesfuly remove from database"}





@app.route("/update_salary", methods=["PUT"])
@auth.login_required
def update_salary():
    data = request.json
    if ("emp_name" in data or "emp_id" in data) and "percentage" in data:
        emps_query = (f"select emp_id, emp_name, salary from company.employess "
                      f"where emp_name = '{data['emp_name']}'")
        emp = company_func.read_from_database(sql_query=emps_query, config=config)[0]
        budget = company_func.read_from_database(
            f"select sum(p.budget) from company.projects p join company.contracts c "
            "on c.project_id = p.project_id join company.employess e "
            f"on e.emp_id = c.emp_id where e.emp_id = {emp['emp_id']}", config)
        new_salary = emp['salary'] + emp['salary'] * float(data['percentage']) / 100

        if new_salary < (budget[0]['sum'] * company_func.budget_cap):
            response = company_func.execute_query(f"UPDATE company.employess "
                                                  f"set salary = {new_salary} where emp_id = {emp['emp_id']}",
                                                  config)
            print(response)
            return {"message": "Employee salary was updating."}
        else:
            print("Not enaugh for the raise !")
            return {"ERROR": "Not enough money"}
    else:
        return {"ERROR": "Mandatory variables were not provided. Please a provide a name or an id"}


if __name__ == '__main__':
    app.run()
