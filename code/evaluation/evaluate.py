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
        self.hardness_error = {"easy": 0,
            		  "medium": 0,
            		  "hard": 0,
            		  "extra": 0}
        
    def turkish_char_analysis(self, str):
    	str = str.replace("FROM İ", "FROM i")
    	str = str.replace("from İ", "from i")
    	str = str.replace("FROM Ü", "FROM ü")
    	str = str.replace("from Ü", "from ü")
    	str = str.replace("FROM Ö", "FROM ö")
    	str = str.replace("from Ö", "from ö")
    	str = str.replace("FROM Ç", "FROM ç")
    	str = str.replace("from Ç", "from ç")
    	str = str.replace("FROM Ş", "FROM ş")
    	str = str.replace("from Ş", "from ş")
    	
    	str = str.replace("JOIN İ", "JOIN i")
    	str = str.replace("join İ", "join i")
    	str = str.replace("JOIN Ü", "JOIN ü")
    	str = str.replace("join Ü", "join ü")
    	str = str.replace("JOIN Ö", "JOIN ö")
    	str = str.replace("join Ö", "join ö")
    	str = str.replace("JOIN Ç", "JOIN ç")
    	str = str.replace("join Ç", "join ç")
    	str = str.replace("JOIN Ş", "JOIN ş")
    	str = str.replace("join Ş", "join ş")
    	
    	str = str.replace("FROM Ref_Şablon_Türleri", "FROM ref_şablon_türleri")
    	str = str.replace("FROM Lise_Öğrencisi", "FROM lise_öğrencisi")
    	str = str.replace("FROM Araba_İmalatçıları", "FROM araba_imalatçıları")
    	str = str.replace("FROM Araba_İsimleri", "FROM araba_isimleri")
    	str = str.replace("FROM Öğrenci_Kayıt_Dersler", "FROM öğrenci_kayıt_dersler")
    	str = str.replace("FROM Transkript_İçeriği", "FROM transkript_içeriği")
    	str = str.replace("FROM Diğer_Mevcut_Özellikler", "FROM diğer_mevcut_özellikler")
    	str = str.replace("FROM Ref_Özellik_Türleri", "FROM ref_özellik_türleri")
    	
    	str = str.replace("JOIN Ref_Şablon_Türleri", "JOIN ref_şablon_türleri")
    	str = str.replace("JOIN Lise_Öğrencisi", "JOIN lise_öğrencisi")
    	str = str.replace("JOIN Araba_İmalatçıları", "JOIN araba_imalatçıları")
    	str = str.replace("JOIN Araba_İsimleri", "JOIN araba_isimleri")
    	str = str.replace("JOIN Öğrenci_Kayıt_Dersler", "JOIN öğrenci_kayıt_dersler")
    	str = str.replace("JOIN Transkript_İçeriği", "JOIN transkript_içeriği")
    	str = str.replace("JOIN Diğer_Mevcut_Özellikler", "JOIN diğer_mevcut_özellikler")
    	str = str.replace("JOIN Ref_Özellik_Türleri", "JOIN ref_özellik_türleri")
    	return str

    def evaluate(self):
        for index, row in self.df.iterrows():
            db = str(row['db_id'])
            hardness = str(row['hardness'])
            gpt = str(row['turkcell']).strip(',.;') # change here !!!!!!!!
            gpt = self.turkish_char_analysis(gpt)
            
            gpt_error = "OK"
            
            query = str(row['query']).strip(',.;')

            if gpt == query:
                self.count += 1
            self.total += 1

            db_path = "../../database/" + db.strip('"') + "/" + db.strip('"') + ".sqlite"
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            result1 = -1
            result2 = 0
            try:
                out = cur.execute(gpt)
                result1 = [o for o in out]
            except Exception as e:
                self.error_count_gpt += 1
                self.hardness_error[hardness] += 1
                print("db", db)
                print("query", query)
                print("gpt", gpt)
                print(e)
                print("--------------------")

            try:
                out = cur.execute(query)
                result2 = [o for o in out]
            except e:
                self.error_count_current += 1
                print(db + " - " + query)
                print(e)

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
        print("Hardness Error:", self.hardness_error)


def main():
    spider_evaluator = SpiderEvaluator("evaluation.xlsx")
    spider_evaluator.evaluate()
    spider_evaluator.print_results()


if __name__ == "__main__":
    main()
