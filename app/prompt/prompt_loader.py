from pathlib import Path


#加载提示词
def load_prompt(name:str)->str:
    path = Path(__file__).parents[2] / "prompt"/f"{name}.prompt"
    return path.read_text(encoding="utf8")

if __name__ == '__main__':
   result= load_prompt("correct_sql")
   print(result)