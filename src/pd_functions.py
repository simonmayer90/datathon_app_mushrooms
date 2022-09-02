import pandas as pd
import numpy as np
import streamlit as st

def get_ready_test(uploaded_file):

    test = pd.read_csv(uploaded_file)
    test.columns = ['id','preds']
    return (
    test
        .assign(
            id = lambda df_: df_['id'].astype('int32'),
            preds = lambda df_: df_['preds'].astype('object'),
            )
        )


def get_metrics(RESULTS_PATH: str, test: pd.DataFrame):

    results = pd.read_csv(RESULTS_PATH)
    results.columns = ['id','real']

    row_evaoluation = (
    results
        .assign(
            id = lambda df_: df_['id'].astype('int32'),
            real = lambda df_: df_['real'].astype('object')
        )
        .merge(test, how='left', on='id')
        .assign(
            correct = lambda df_: df_['real'] == df_['preds'], 
            deads = lambda df_: np.where((df_['real']==1) & (df_['preds']==0), True, False),
            opportunity_cost = lambda df_: np.where((df_['real']==0) & (df_['preds']==1), True, False) 
            )
        .agg({
            'correct':'sum',
            'deads':'sum',
            'opportunity_cost':'sum'
            })
        )

    return (
    pd.DataFrame([[
        st.session_state.text_input, 
        row_evaoluation['correct']/results.shape[0], 
        row_evaoluation['deads'], 
        row_evaoluation['opportunity_cost'],
        pd.Timestamp.now()
        ]], 
        columns=['participant','accuracy','deads','opportunity_cost', 'submission_time'])
        )


def plot_confusion_marix(df_: pd.DataFrame): 
    
    (
    df_
        .groupby(['real','preds'])
        .agg(count = ('id','count'))
        # .reset_index()
        # .pivot(index='real', columns='preds', values='count')
    )


def plot_submissions(): 
    
    participant_submissions = (
        pd.read_pickle('files_to_update/submissions.pkl')
            .query('participant == @st.session_state.text_input')
            .filter(['submission_time','deads'])
            .set_index('submission_time')
            .copy()
        )
    if participant_submissions.shape[0] > 1:
        st.line_chart(participant_submissions)
    else: 
        st.success('Congratulations on your first submission!')


def update_submissions(participant_results: pd.DataFrame):

    (
        pd.concat([
            pd.read_pickle('files_to_update/submissions.pkl'), 
            participant_results
        ])
        .to_pickle('files_to_update/submissions.pkl')
    )


def show_leaderboard(): 

    st.title('LEADERBOARD')

    st.dataframe(
    pd.read_pickle('files_to_update/submissions.pkl')
        .assign(attempts = lambda df_: df_.groupby('participant')['participant'].transform('count'))
        .sort_values(['deads','opportunity_cost'], ascending=[True, True, False])
        .drop_duplicates(['participant'], keep='first')
        .assign(position = lambda df_: range(1, len(df_)+1)) 
        .set_index('position')  
        .filter(['participant','deads','opportunity_cost','accuracy','attempts'])
    )
