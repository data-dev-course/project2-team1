from jinja2 import Environment, FileSystemLoader
import yaml
import os

file_dir = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(file_dir))
template = env.get_template("chart_templated_dag.jinja2")


with open(f"{file_dir}/config_chart.yml", "r") as cf:
    config = yaml.safe_load(cf)

chart_dic_list = config["chart_data"]

for i, chart_dic in enumerate(chart_dic_list):
    chart_dic["schedule"] = None
    if i + 1 != len(chart_dic_list):
        chart_dic["call_trigger"] = ">> trigger"
        chart_dic["trigger_chart_num"] = chart_dic_list[i + 1]["chart_num"]
    with open(
        f"dags/dynamic_dags/Daily_Bigquery_to_Firestore_{chart_dic['chart_num']}.py",
        "w",
    ) as f:
        f.write(template.render(chart_dic))
