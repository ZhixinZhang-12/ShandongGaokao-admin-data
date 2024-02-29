import pandas as pd



def find_employees(Employee: pd.DataFrame) -> pd.DataFrame:

    Employee_with_manager = Employee.merge(Employee, left_on='managerId', right_on='id', suffixes=('_emp', '_mgr'))

    compframe=pd.merge(left=Employee,right=Employee,how="left",left_on="managerId",right_on="id",suffixes=('1','2'))

# 筛选出收入比经理高的员工

    Employee_with_higher_salary = Employee_with_manager[Employee_with_manager['salary_emp'] > Employee_with_manager['salary_mgr']]



# 返回结果表，只保留员工的 id 和 name 列

    result = Employee_with_higher_salary[[ 'name_emp']].rename(columns={'name_emp': 'Employee'})

    return result
data = [[1, 'Joe', 70000, 3], [2, 'Henry', 80000, 4], [3, 'Sam', 60000, None], [4, 'Max', 90000, None]]
employee = pd.DataFrame(data, columns=['id', 'name', 'salary', 'managerId']).astype({'id':'Int64', 'name':'object', 'salary':'Int64', 'managerId':'Int64'})
compframe=pd.merge(left=employee,right=employee,how="inner",left_on="managerId",right_on="id",suffixes=('1','2'))
name1=compframe[compframe['salary1']>compframe['salary2']][['name1']].rename(columns={'name1': 'Employee'})
print(name1)

