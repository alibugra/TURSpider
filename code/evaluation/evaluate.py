import pandas as pd
import sqlite3


class SpiderEvaluator:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = pd.read_excel(excel_path)
        self.count = 0
        self.total = 0
        self.number_of_correct = 0
        self.error_count_current = 0
        self.error_count_gpt = 0
        
        self.hardness_dict = {"easy": 0,
            		       "medium": 0,
            		       "hard": 0,
            		       "extra": 0}

    def evaluate(self, llm_name):
        for index, row in self.df.iterrows():
            db = str(row['Database'])
            hardness = str(row['hardness'])
            gpt = str(row[llm_name]).strip('",.;').lower() # change here !!!!!!!!
            gpt = gpt.replace("\\n", " ")
            
            # error_fix = str(row[llm_name + '_error_fix']).strip('",.;').lower()
            # error_fix = error_fix.replace("\\n", " ")
            error_fix = "ok"
            
            # gpt = gpt.replace("\\", " ")
            query = str(row['Query'])[1:-1].strip(',.;').lower()

            if gpt == query:
                self.count += 1
            self.total += 1

            db_path = "spider/database/" + db.strip('"') + "/" + db.strip('"') + ".sqlite"
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            result1 = -1
            result2 = 0
            try:
                if error_fix == "ok":
                    out = cur.execute(gpt)
                    result1 = [o for o in out]
                    print("OK") # USE IT FOR ONLY ERROR ANALYSIS
                else:
                    out = cur.execute(error_fix)
                    result1 = [o for o in out]
            except Exception as e:
                self.error_count_gpt += 1
                print(e)

            try:
                out = cur.execute(query)
                result2 = [o for o in out]
            except:
                self.error_count_current += 1

            if result1 == result2:
                self.number_of_correct += 1
                self.hardness_dict[hardness] += 1

            con.close()

    def print_results(self):
        print("Number of correct:", self.number_of_correct)
        print("LFA:", self.count / self.total)
        print("EX:", self.number_of_correct / (self.total - self.error_count_current))
        print("EX:", self.number_of_correct / self.total)
        print("Error count current:", self.error_count_current)
        print("Error count LLM:", self.error_count_gpt)
        
        print("Hardness Dict:", self.hardness_dict)
        print("Hardness Dict Easy:", self.hardness_dict["easy"] / 248)
        print("Hardness Dict Medium:", self.hardness_dict["medium"] / 446)
        print("Hardness Dict Hard:", self.hardness_dict["hard"] / 174)
        print("Hardness Dict Extra:", self.hardness_dict["extra"] / 166)


def main():
    spider_evaluator = SpiderEvaluator("evaluation.xlsx") # includes predicted and actual SQL queries
    spider_evaluator.evaluate('model_name') 
    spider_evaluator.print_results()


if __name__ == "__main__":
    main()
