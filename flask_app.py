from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.datastructures import auth
import json
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


@app.route("/departments")
def show_all_departments() -> dict:
    departments = company_func.read_from_database(sql_query="select departament_id,departament_name "
                                                            "from company.departments order by departament_id",
                                                  config=config)
    return departments


# create a post request that allows to hire new employees.  with auth
@app.route("/hire_employee", methods=['POST'])
@auth.login_required
def hire_new_employee():
    try:
        data = request.json
        if "emp_name" in data and "date_of_birth" in data and "salary" in data and "starting_date" in data and "departament_id" in data:
            company_func.execute_query(f"INSERT into company.employess "
                                       f"(emp_name,date_of_birth,salary,starting_date,department_id) "
                                       f"values('{data['emp_name']}', '{data['date_of_birth']}', {data['salary']}, "
                                       f"'{data['starting_date']}', {data['departament_id']})", config)

        return {"message": "Succesfuly hire new employee"}
    except Exception as e:
        return {"ERROR": f"404 NOT FOUND {e}"}


@app.route("/show_employees_with_dapartment/<department_id>")
def show_employees_with_dapartment(department_id: int):
    emps = company_func.read_from_database(sql_query=f"select emp_id, emp_name from company.employess "
                                                     f"where department_id = {department_id}",
                                           config=config)
    return emps


# create a put request to change the budget of a project . with auth
@app.route("/change_budget/<project_id>", methods=['PUT'])
@auth.login_required
def change_budget(project_id: int):
    try:
        data = request.json
        if "budget" in data:
            company_func.execute_query(f"UPDATE company.projects set budget = {data['budget']} "
                                       f"where project_id = {project_id}",
                                       config)
            return {"message": "Successfuly update the budget"}
    except Exception as e:
        return {"ERROR": f"404 NOT FOUND {e}"}


# create a get that returns the average budget for all projects
@app.route("/avg_budget")
def avg_budget_for_all_projects():
    avg_budget = company_func.read_from_database("select avg(budget) from company.projects", config)

    return {"avg_budget": avg_budget}


# create a post request that creates new contracts for employees( give them a new project)
@app.route("/create_contracts/<emp_id>", methods=['POST'])
@auth.login_required
def create_contracts(emp_id: int):
    try:
        data = request.json
        if "project_name" in data and "budget" in data and "deadline" in data:
            project_query = (f"INSERT INTO company.projects(project_name,budget,deadline) "
                             f"values('{data['project_name']}', {data['budget']}, '{data['deadline']}')")
            company_func.execute_query(project_query, config)

            project_id_result = company_func.read_from_database("select * from company.projects order by project_id", config)
            project_id = project_id_result[-1]['project_id']

            company_query = (f"INSERT INTO company.contracts (contract_name,finishing_date,project_id,emp_id)"
                             f" values('{'Contract ' + data['project_name']}', '{data['deadline']}', "
                             f"{project_id}, {emp_id})")
            company_func.execute_query(company_query, config)

            return {"message": "Succesfuly create a new contract"}
    except Exception as e:
        return {"ERROR": f"404 NOT FOUND {e}"}


if __name__ == '__main__':
    app.run()
