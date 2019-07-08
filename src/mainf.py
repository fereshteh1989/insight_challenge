class Report:
  # This class keeps track of all product and order information provided by input files
    def __init__(self):
        self.departments =[Department(0)]
        self.itemz = {}
        self.deptIDs = []
  # If a department appears in product.csv it will be added to Report object
    def addDepartment(self,department):
        self.departments.append(department)
        self.deptIDs.append(department.ID)
  # Create a dictionary for fast access of department id for any given product id
    def addItem(self,prod_id,dept_id):
        self.itemz[prod_id] = dept_id

  # Get a department id and return its index in the Report object storage
    def getDeptIndex(self,deptid):
        #Gets department ID, returns department index
        for d in self.departments:
            if d.ID == deptid:
                return self.departments.index(d)
        return 0
   # Get a product id and return its corresponding department id
    def getDeptId(self,prod_id):
        if prod_id not in self.itemz.keys():
            return 0
        return self.itemz[prod_id]
   # Return a sorted list of department ids
    def sortDepts(self):
        return sorted(self.deptIDs)
   # Create report file and populate
    def makeReport(self):
        deptids = list(self.sortDepts())
        path3 = os.path.abspath("../output/report.csv")
        with open(path3, 'w', newline='') as csvfile:
            reporter = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
            reporter.writerow(['department_id'] + ['number_of_orders']+['number_of_first_orders']+['percentage'])
            for id in deptids:
                ind = self.getDeptIndex(id)
                self.departments[ind].calcTotals()
                if self.departments[ind].totalOrder > 0:
                    reporter.writerow([('%d')%(self.departments[ind].ID)]+[('%d')%(self.departments[ind].totalOrder+self.departments[ind].totalReorder)]+[('%d')%(self.departments[ind].totalOrder)]+[('%s')%(round(self.departments[ind].totalOrder/(self.departments[ind].totalOrder+self.departments[ind].totalReorder),2))])
                else:
                    continue
        
        print('Since the web-based test environment does not seem to "see" my output file, Im reading the info back from the report.csv file and printing them!')
        with open(path3, encoding="utf8") as csvfile:
            tester = csv.reader(csvfile,delimiter =',')
            for row in tester:
                print(row)


class Product:
    # This class keeps track of products, their department numebr, and the number of times they were (re)ordered
    # While for the purpose of this challenge keeping track of individual products might not be necessary, I still
    # preferred to have it since this way the code can be modified to report much more detailed data
    def __init__(self,ID,ordered,reordered,dept):
        self.ID = ID
        self.ordered = ordered
        self.reordered = reordered
        self.department = dept

    # Increase the number of orders and/or reorders for individual produts
    def increase(self,ordered,reordered):
        #print('Increasing order number for product number %d from %d'%(self.ID,self.ordered))
        self.ordered += 1
        self.reordered += reordered

class Department:
    # This class keeps track of individual departments, their id, their products, and the total number of (re)orders from each department
    def __init__(self,id):
        self.ID = id
        self.products = []
        self.totalOrder = 0
        self.totalReorder = 0

    # Adding a product to the department, object of Product class
    def addProduct(self,product):
        self.products.append(product)

    # Get the index of a product using its id, if the product is already added to this department
    def getProdIndex(self,id):
        for p in self.products:
            if p.ID == id:
                return self.products.index(p)
        return 0

    # Calculating the total number of (re)orders for this department
    def calcTotals(self):
        for p in self.products:
            self.totalOrder += p.ordered
            self.totalReorder +=p.reordered
import csv
import os

report = Report()

#Adding products and departments to the main Report object
path = os.path.abspath("../input/products.csv")
with open(path, encoding="utf8") as csvfile:
    product_info = csv.DictReader(csvfile)
    for row in product_info:
        dept_id = int(row['department_id'])
        prod_id = int(row['product_id'])
        deptind = report.getDeptIndex(dept_id)

        #If department is already added, just add the product to that department
        if deptind:
            report.departments[deptind].addProduct(Product(prod_id,0,0,dept_id))
            report.addItem(prod_id,dept_id)
        #If the department is not added, add the department, and then add the product
        else:
            report.addDepartment(Department(dept_id))
            deptind = len(report.departments)-1#report.getDeptIndex(int(row['department_id']))
            report.departments[deptind].addProduct(Product(prod_id,0,0,dept_id))
            report.addItem(prod_id,dept_id)

#Now adding order and re-order info to the individual products
path2 = os.path.abspath("../input/order_products.csv")
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
