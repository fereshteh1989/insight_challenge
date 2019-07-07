class Report:
    def __init__(self):
        self.departments =[Department(0)]
        self.itemz = {}
        self.deptIDs = []

    def addDepartment(self,department):
        self.departments.append(department)
        self.deptIDs.append(department.ID)

    def addItem(self,prod_id,dept_id):
        self.itemz[prod_id] = dept_id


    def searchProdIDs(self,id):
        #Gets product ID, returns department ID
        for d in self.departments:
            for p in d.products:
                if p.ID == id:
                    return (d.ID)
        return 0

    def getDeptIndex(self,deptid):
        #Gets department ID, returns department index
        for d in self.departments:
            if d.ID == deptid:
                return self.departments.index(d)
        return 0

    def getDeptId(self,prod_id):
        if prod_id not in self.itemz.keys():
            return 0
        return self.itemz[prod_id]

    def sortDepts(self):
        return sorted(self.deptIDs)

    def makeReport(self):
        deptids = list(self.sortDepts())
        print(deptids)
        path3 = Path(__file__).parent.resolve().parent/'output/report.csv'
        with open(path3, 'w', newline='') as csvfile:
            reporter = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
            reporter.writerow(['department_id'] + ['number_of_orders']+['number_of_first_orders']+['percentage'])
            for id in deptids:
                ind = self.getDeptIndex(id)
                self.departments[ind].calcTotals()
                if self.departments[ind].totalOrder > 0:
                    reporter.writerow([('%d')%(self.departments[ind].ID)]+[('%d')%(self.departments[ind].totalOrder+self.departments[ind].totalReorder)]+[('%d')%(self.departments[ind].totalOrder)]+[('%s')%(round(100*self.departments[ind].totalReorder/(self.departments[ind].totalOrder+self.departments[ind].totalReorder),2))])
                else:
                    continue


class Product:
    def __init__(self,ID,ordered,reordered,dept):
        self.ID = ID
        self.ordered = ordered
        self.reordered = reordered
        self.department = dept

    def increase(self,ordered,reordered):
        #print('Increasing order number for product number %d from %d'%(self.ID,self.ordered))
        self.ordered += 1
        self.reordered += reordered

class Department:
    def __init__(self,id):
        self.ID = id
        self.products = []
        self.totalOrder = 0
        self.totalReorder = 0

    def addProduct(self,product):
        self.products.append(product)

    def getProdIndex(self,id):
        for p in self.products:
            if p.ID == id:
                return self.products.index(p)
        return 0
    def calcTotals(self):
        for p in self.products:
            self.totalOrder += p.ordered
            self.totalReorder +=p.reordered
import csv
import os
from pathlib import Path

report = Report()
#Adding products and departments to the main report
path = Path(__file__).parent.resolve().parent/'input/products.csv'
#path = os.path.join(Path(__file__).parent.resolve().parent,'\\input\\product.csv')

with open(path, encoding="utf8") as csvfile:
    product_info = csv.DictReader(csvfile)
    for row in product_info:
        #Search 1: find index - fairly small
        dept_id = int(row['department_id'])
        prod_id = int(row['product_id'])
        deptind = report.getDeptIndex(dept_id)

        #If department is already added, just add the product to that department
        if deptind:
            report.departments[deptind].addProduct(Product(prod_id,0,0,dept_id))
            report.addItem(prod_id,dept_id)
        #If the department is not added, add the department, and then add the department
        else:
            report.addDepartment(Department(dept_id))
            deptind = len(report.departments)-1#report.getDeptIndex(int(row['department_id']))
            report.departments[deptind].addProduct(Product(prod_id,0,0,dept_id))
            report.addItem(prod_id,dept_id)

#Now adding order and re-order info to the products
path2 = Path(__file__).parent.resolve().parent/'input/order_products.csv'
with open(path2) as csvfile:
    order_info = csv.reader(csvfile, delimiter = ',')
    new_count = 0
    next(order_info)
    for row in order_info:
        new_count += 1
        if row[1] == '':
            break
        prod_id = int(row[1])
        reordered = int(row[3])
        #Search 2: find department id for a product - very large - I can use a dictionary instead that maps product to department id
        deptID = report.getDeptId(prod_id)
        if deptID:
            #Search 3: REPEAT SEARCH. Get index. Fairly small.
            deptIndex = report.getDeptIndex(deptID)
            prodIndex = report.departments[deptIndex].getProdIndex(prod_id)
            report.departments[deptIndex].products[prodIndex].increase(1,reordered)
        else:
            print('Unknown product! Order information dismissed!')
            #report.addProduct(Product(int(row[1]),1,int(row[3]),0))
report.makeReport()
