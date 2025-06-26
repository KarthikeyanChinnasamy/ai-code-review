import os

import about
import display
import download
import forms
import query
import repo
import streamlit as st
import utils
import shutil
import threading
import time
import configparser

config = configparser.ConfigParser()
config.read(os.getcwd() + '/config/ctbidsai.config')

env_file_path = ".env"
log_file = "app.log"

temp_dir = config.get('config', 'temp_dir')

def clean_temp_dir():
    while True:
        if os.path.exists(temp_dir):
            print(f"[CLEANUP] Clearing: {temp_dir}")
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Failed to delete {item_path}: {e}")
        # time.sleep(300)  # 5 minutes
        time.sleep(60)  # 1 minutes

# import shutil

# # Define the temporary directory path dynamically
# temp_dir = "/tmp/chatgpt-code-review"
# main_file_path = os.path.join(temp_dir, "main.py")

# # Ensure the temporary directory exists
# os.makedirs(temp_dir, exist_ok=True)

# # Ensure the `main.py` file exists
# source_main_file = os.path.join(os.getcwd(), "main.py")  # Adjust to your source location
# if not os.path.exists(main_file_path):
#     if os.path.exists(source_main_file):
#         shutil.copy(source_main_file, main_file_path)
#         print(f"Copied {source_main_file} to {main_file_path}")
#     else:
#         with open(main_file_path, "w") as f:
#             f.write("# Placeholder for main.py\n")
#             f.write("print('Hello from dynamically created main.py')")
#         print(f"Created placeholder main.py at {main_file_path}")


def app():
    utils.load_environment_variables(env_file_path)
    utils.set_environment_variables()
    utils.configure_logging(log_file)
    # threading.Thread(target=clean_temp_dir, daemon=True).start()

    with utils.TempDirContext(temp_dir):
        st.set_page_config(
            page_title="ChatGPT Code Review",
        )

        session_state = st.session_state

        # st.title("ChatGPT Code Review :rocket:")
        st.title("Code Review 🛠️💻")

        with st.expander("About Code Review"):
            st.markdown(about.about_section, unsafe_allow_html=True)
            st.write("")

        default_repo_url = "https://github.com/your_code_review/repository"
        repo_form = forms.RepoForm(default_repo_url)
        with st.form("repo_url_form"):
            repo_form.display_form()

        # # Check if the API key is valid before proceeding
        # if repo_form.clone_repo_button and not repo_form.is_api_key_valid():
        #     st.stop()

        # repo_url, extensions = repo_form.get_form_data()

        form_data = repo_form.get_form_data()
        if len(form_data) == 2:
            repo_url, extensions = form_data
            password = None
            branch = None
        elif len(form_data) == 3:  # Includes username and password
            # repo_url, username, password, extensions = form_data
            repo_url, extensions, password = form_data
            # print("extensions: ")
            # print(extensions)
            # print("\n")
            branch = None
        elif len(form_data) == 4:  # Includes username and password
            # repo_url, username, password, extensions = form_data
            repo_url, extensions, password, branch = form_data
            # print("extensions: ")
            # print(extensions)
            # print("\n")
        else:
            st.error("Invalid form data received. Please fill out all required fields.")
            return
        # else:  # No authentication needed
        #     repo_url, extensions = form_data
        #     # print("extensions: ")
        #     # print(extensions)
        #     # print("\n")
        #     # username, password = None, None
        #     password = None
        #     branch = None


        analyze_files_form = forms.AnalyzeFilesForm(session_state)
        with st.form("analyze_files_form"):
            if repo_form.clone_repo_button or session_state.get("code_files"):
                if not session_state.get("code_files"):
                    # password = None
                    # if "@" in repo_url or st.checkbox("Does the repository require authentication?"):
                    #     password = st.text_input("Password (if required):", type="password")

                    if password and branch:
                        # print("repo_url_3: ", repo_url)
                        # print("\n")
                        # print("extensions_3: ", extensions)
                        # print("\n")
                        # print("password_2: ", password)
                        # print("\n")
                        # print("branch_2: ", branch)
                        # print("\n")
                        session_state.code_files = repo.list_code_files_in_repository(
                            repo_url, extensions, password, branch
                        )
                    elif password:
                        # print("repo_url_1: ", repo_url)
                        # print("\n")
                        # print("extensions_1: ", extensions)
                        # print("\n")
                        # print("password_1: ", password)
                        # print("\n")
                        session_state.code_files = repo.list_code_files_in_repository(
                            repo_url, extensions, password
                        )
                    elif branch:
                        # print("repo_url_2: ", repo_url)
                        # print("\n")
                        # print("extensions_2: ", extensions)
                        # print("\n")
                        # print("branch_1: ", branch)
                        # print("\n")
                        session_state.code_files = repo.list_code_files_in_repository(
                            repo_url, extensions, branch
                        )
                    else:
                        # print("repo_url_4: ", repo_url)
                        # print("\n")
                        # print("extensions_4: ", extensions)
                        # print("\n")
                        session_state.code_files = repo.list_code_files_in_repository(
                            repo_url, extensions
                        )

                    del password

                analyze_files_form.display_form()

        # Analyze the selected files
        with st.spinner("Analyzing files..."):
            if session_state.get("analyze_files"):
                if session_state.get("selected_files"):
                    recommendations = query.analyze_code_files(
                        session_state.selected_files
                    )

                    # Display the recommendations
                    st.header("Recommendations")
                    first = True
                    recommendation_list = []
                    for rec in recommendations:
                        if not first:
                            st.write("---")
                        else:
                            first = False
                        st.subheader(display.escape_markdown(rec["code_file"]))
                        recommendation = (
                            rec["recommendation"] or "No recommendations"
                        )
                        st.markdown(recommendation)
                        with st.expander("View Code"):
                            extension = os.path.splitext(rec["code_file"])[1]
                            display.display_code(
                                rec["code_snippet"], extension
                            )
                        recommendation_list.append(rec)
                    if recommendation_list:
                        session_state.recommendation_list = recommendation_list
                else:
                    st.error("Please select at least one file to analyze.")
                    st.stop()

        st.write("")

        download.download_markdown(session_state.get("recommendation_list"))


if __name__ == "__main__":
    app()
