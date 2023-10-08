from pipeline.pipeline_factory import create_pipeline
import logging
from pipeline.pipeline import generate_task_id
import os
import argparse
from utils.config_center import Config

def search(topic):
    # setup logging
    task_id = generate_task_id(topic)
    log_file_path = os.path.join(os.path.dirname(
        __file__), "output", task_id, "search.log")
    if not os.path.exists(os.path.dirname(log_file_path)):
        os.makedirs(os.path.dirname(log_file_path))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path, encoding="utf-8")
        ]
    )
    p = create_pipeline()
    pdf, md = p.do_research(topic)
    return pdf, md, p.get_bill(topic)

DONE_LOGO = """
                 ,----..            ,--.           
    ,---,       /   /   \         ,--.'|    ,---,. 
  .'  .' `\    /   .     :    ,--,:  : |  ,'  .' | 
,---.'     \  .   /   ;.  \,`--.'`|  ' :,---.'   | 
|   |  .`\  |.   ;   /  ` ;|   :  :  | ||   |   .' 
:   : |  '  |;   |  ; \ ; |:   |   \ | ::   :  |-, 
|   ' '  ;  :|   :  | ; | '|   : '  '; |:   |  ;/| 
'   | ;  .  |.   |  ' ' ' :'   ' ;.    ;|   :   .' 
|   | :  |  ''   ;  \; /  ||   | | \   ||   |  |-, 
'   : | /  ;  \   \  ',  / '   : |  ; .''   :  ;/| 
|   | '` ,/    ;   :    /  |   | '`--'  |   |    \ 
;   :  .'       \   \ .'   '   : |      |   :   .' 
|   ,.'          `---`     ;   |.'      |   | ,'   
'---'                      '---'        `----'     
                                                   """


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='tool')
    parser.add_argument('-t', '--topic', type=str, help='topic to research')
    parser.add_argument('-o', '--output-dir', type=str, default=os.getcwd(), help='output dir to save md and pdf file')
    parser.add_argument('--disable-headless', action='store_true', help='disable headless mode for selenium, useful for debug')
    args = parser.parse_args()
    topic = args.topic
    Config().set_global_config("disable_headless", args.disable_headless)
    try:
        pdf_path, md_path, bill = search(topic)
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        import shutil
        name = generate_task_id(topic)
        shutil.copy(pdf_path, os.path.join(args.output_dir, generate_task_id(topic) + ".pdf"))
        shutil.copy(md_path, os.path.join(args.output_dir, generate_task_id(topic) + ".md"))
        
        print(DONE_LOGO)
        print(f"task finished, report LLM charges a total of {bill.total_bill} dollars.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"task failed: {e}")
