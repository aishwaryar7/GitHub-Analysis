from flask import Flask, render_template, request
import requests
from getpass import getpass
import json
from github import Github
from scipy.stats import rankdata
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral10,Category20c
from bokeh.plotting import figure
from bokeh.models import Legend
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from plotly.offline import plot
from plotly.graph_objs import Scatter
from markupsafe import Markup, escape
import io
import base64
import networkx as nx

g = Github("aebf2c813b4d40cd2832b0fff6bfa744c090a5c5")
app = Flask(__name__)

# language code
warnings.filterwarnings("ignore")
data =  pd.read_csv('github_data.csv')
data.drop_duplicates().head()

data = data[data.Language != "None"]
data.head()

year_language = data.groupby(['Language']).count()
top_languages = year_language.nlargest(10, columns = 'Repository' )
languages = top_languages.index
top_languages = top_languages['Repository']
languages_count = top_languages.values
# print("l",languages_count)

j = 1
modified = []
rank_list = []
color = []

output_file("bars.html")

def cal(maxi,j,rank_list,modified):
    if(len(rank_list) > 0):
        for i in rank_list:
            if(i == maxi):
                modified.append(j)
                rank_list.remove(i)
                cal(maxi,j,rank_list,modified)
            else:
                maxi = max(rank_list)
                j = j+1
                cal(maxi,j,rank_list,modified)

@app.route('/')
def student():
   return render_template('index.html')

@app.route('/repository',methods = ['POST', 'GET'])
def repositoryresult():
   if request.method == 'POST':
      result = request.form
#       print(result)
      for k,v in result.items():
        username = v
        user2 = g.get_user(username)
        repositories = user2.get_repos()
        ranks = []
        repo_names = []
        dictionary = {}
        for repo in repositories:
            count_issues = repo.open_issues_count
            count_stars = repo.stargazers_count
            count_fork = repo.forks_count
            #print("issues",count_issues," ", "stars",count_stars," ","forked",count_fork)
            repo_rank = (count_fork + count_stars - count_issues)
            ranks.append(repo_rank)
            repo_names.append(repo.name)
            #print("score",repo_rank," ","name:",repo.name," ","forked",bool(repo.fork))
            dictionary[repo.name] = repo_rank


        modified = []
        rank_list = []
        color = []
        l = sorted(dictionary.items(), key=lambda kv: kv[1], reverse=True)
        rang = list(range(1,11))
        list_rang = [str(i)for i in rang]

        b = [x[0]  for x in l]
        input = [x[1] for x in l]
        #print(input)
        a = rankdata(input, method='dense')
        list_of_ranks = a.tolist()
        #print("listofranks",list_of_ranks)
            #b[:5]

        rank_list = list_of_ranks[:10] 
        maxi = max(list(rank_list))
        cal(maxi,j,rank_list,modified)
        #print("modified",modified)


        for i in modified:
            if(i == 1):
                    color.append(Spectral10[0])
            if(i == 2):
                    color.append(Spectral10[1])
            if(i == 3):
                    color.append(Spectral10[2])
            if(i == 4):
                    color.append(Spectral10[3])
            if(i == 5):
                    color.append(Spectral10[4])
            if(i == 6):
                    color.append(Spectral10[5])
            if(i == 7):
                    color.append(Spectral10[6])
            if(i == 8):
                    color.append(Spectral10[7])
            if(i == 9):
                    color.append(Spectral10[8])
            if(i == 10):
                    color.append(Spectral10[9])
                    
        source = ColumnDataSource(data=dict(repo_names= b[:10], counts=list_of_ranks[:10],ranks=modified ,color=color))

        p = figure(x_range=b[:10],plot_width = 800,plot_height=600, title="Top 10 Repository",
                    toolbar_location=None, tools="")

        p.vbar(x='repo_names', top='counts', width=0.4,color='color',legend='ranks',source=source)

        p.xaxis.major_label_orientation = "vertical"
        p.xaxis.axis_label = 'Repository Names'
        p.yaxis.axis_label = 'Score'
        p.xgrid.grid_line_color = None
        p.legend.orientation = "horizontal"
        p.legend.location = "top_right"

        show(p)
      return render_template("index.html")

@app.route('/language',methods = ['POST', 'GET'])
def langresult():
        

        if request.method == 'POST':
                plt.clf()
                result = request.form
                lang =''
                # print(result)
                for k,v in result.items():
                        lang = v
                to_plot = pd.Series()
                names = []
        
                if lang == "All":
                        '''for i in range(10):
                                to_plot = getCount(languages[i],data)
                                year = to_plot.index
                                values = to_plot.values
                                plt.plot()
                                names.append(languages[i])
                                plt.legend(names)
                        plt.xlabel('Years')
                        plt.ylabel('Count')
                        plt.title('Trending Languages')
                        
                        img = io.BytesIO()

                        plt.savefig(img, format='png')
                        img.seek(0)

                        plot_url = base64.b64encode(img.getvalue()).decode()

                        return '<img src="data:img/png;base64,{}">'.format(plot_url)'''
                        return render_template('all_languages.html')
                
                else:
                        to_plot = getCount(lang, data)
                        year = to_plot.index # X-axis
                        values = to_plot.values # Y-axis
                        to_plot.plot()
                        plt.legend([lang])
                        plt.xlabel('Years')
                        plt.ylabel('Count')
                        plt.title('Trend Chart for ' + lang)
                        
                        img1 = io.BytesIO()

                        plt.savefig(img1, format='png')
                        img1.seek(0)

                        plot_url = base64.b64encode(img1.getvalue()).decode()
                        return '<img src="data:img1/png;base64,{}">'.format(plot_url)
                        
def getCount(lang,data):
    getLanguage = data.loc[data['Language'] == lang]
    getLanguage['Created_On'] = pd.to_datetime(getLanguage['Created_On'])
    year_language = getLanguage['Created_On'].groupby([getLanguage.Created_On.dt.year]).count()

    return year_language

@app.route('/year',methods = ['POST', 'GET'])
def year():
	plt.clf()
	output_file("pie.html")
	labels = languages
	sizes = languages_count
	
	explode = (0,0.1,0,0,0,0,0,0,0,0)  
	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, labels=labels, autopct='%1.1f%%', pctdistance=0.9, labeldistance  = 1.05,
			shadow=True, startangle=90, colors = Spectral10)
	# Equal aspect ratio ensures that pie is drawn as a circle
	ax1.axis('equal')  
	plt.tight_layout()
	plt.rcParams['font.size'] = 8.0
	plt.title('Languages by Popularity')
			
	image = io.BytesIO()

	plt.savefig(image, format='png')
	image.seek(0)

	plot_url = base64.b64encode(image.getvalue()).decode()

	return '<img src="data:image/png;base64,{}">'.format(plot_url)
    
@app.route('/network',methods = ['POST', 'GET'])
def network():
        if request.method == 'POST':
                plt.clf()
                result = request.form
                username = ''
                for k,v in result.items():
                        username = v

                user = g.get_user(username)
                repos = user.get_repos()
                followers=[]
                for follower in user.get_followers():
                        if(follower.name is None ):
                                followers.append(follower.login)
                        else:
                                followers.append(follower.name)
                followers_len=len(followers)
                followers_prev=followers.copy()

                followings=[]
                for following in user.get_following():
                        if(following.name is None ):
                                followings.append(following.login)
                        else:
                                followings.append(following.name)
                followings_len=len(followings)
                followings_prev=followings.copy()

                common=[]
                common=list(set(followers).intersection(followings))
                common_len=len(common)

                for i in common:
                        followers.remove(i)
                        followings.remove(i)

                user=0
                followers_start=1
                followers_end=followers_len + 1
                followings_start=1 + followers_len + 1
                followings_end=1 + followers_len + followings_len + 1
                common_start=1 + followers_len + followings_len + 1
                common_end= 1 + followers_len + followings_len + 1 + common_len

                G = nx.Graph()
                labels = {}

                G.add_node(user)
                labels[user] = user

                for i in range(followers_start, followers_end):
                        G.add_node(i)
                        G.add_edge(0, i)
                        labels[i] = i

                for i in range(followings_start, followings_end):
                        G.add_node(i)
                        G.add_edge(0, i)
                        labels[i] = i

                for i in range(common_start, common_end):
                        G.add_node(i)
                        G.add_edge(0, i)
                        labels[i] = i

                #partition = community.best_partition(G)  # compute communities
                pos = nx.spring_layout(G)

                nx.draw_networkx_nodes(G, pos,
                                nodelist=[user],
                                node_color='#99FFFF',
                                node_size=500,
                                alpha=1.0, label='User')

                nx.draw_networkx_nodes(G, pos,
                                nodelist=range(followers_start, followers_end),
                                node_color='#FFCCFF',
                                node_size=100,
                                alpha=1.0, label='Followers')

                nx.draw_networkx_nodes(G, pos,
                                nodelist=range(followings_start, followings_end),
                                node_color='#99CCFF',
                                node_size=100,
                                alpha=1.0, label='Following')

                nx.draw_networkx_nodes(G, pos,
                                nodelist=range(common_start,
                                                common_end),
                                node_color='#9999FF',
                                node_size=100,
                                alpha=1.0, label='Follower+Following')

                followers_edges = []
                for i in range(followers_start, followers_end):
                        followers_edges.append((user, i))

                followings_edges = []
                for i in range(followings_start, followings_end):
                       followings_edges.append((user, i))

                common_edges = []
                for i in range(common_start, common_end):
                        common_edges.append((user, i))

                nx.draw_networkx_edges(G, pos,
                                edgelist=followers_edges,
                                width=1, alpha=0.8, edge_color='#FFCCFF')
                nx.draw_networkx_edges(G, pos,
                                edgelist=followings_edges,
                                width=1, alpha=0.8, edge_color='#99CCFF')
                nx.draw_networkx_edges(G, pos,
                                edgelist=common_edges,
                                width=1, alpha=0.8, edge_color='#9999FF')

                plt.title('Network Graph of a User and its Followers and whom its Following on Github')
                plt.legend(loc='upper left', bbox_to_anchor=(1,1),labelspacing=1.5, borderpad=1)
                plt.tight_layout()
                plt.axis('off')
                #plt.show()
                networkimg = io.BytesIO()

                plt.savefig(networkimg, format='png')
                networkimg.seek(0)

                plot_url = base64.b64encode(networkimg.getvalue()).decode()
                image1 = "data:image/png;base64,"+format(plot_url)
                #return'<img src="data:image1/png;base64,{}">'.format(plot_url)
                plt.clf()
                return render_template('network.html',plot = image1, repositories=repos, user=username)


@app.route('/eachrepo/<string:reponame>/<string:userName>')
def eachrepo(reponame,userName):
        plt.clf()
#         print(reponame)
#         print(userName)
        user = g.get_user(userName)
        repos1=user.get_repo(reponame)

        repos=[]
        repos.append(repos1)
        contributors=repos[0].get_contributors()
        contributors=list(contributors)
        contributors_len=len(contributors)

        forks=repos[0].forks_count

        stars=repos[0].get_stargazers()
        stars=list(stars)
        stars_len=len(stars)

        repos[0]=0
        contributors_start=1
        contributors_end=contributors_len + 1
        forks_start=1 + contributors_len + 1
        forks_end=1 + contributors_len + forks + 1
        stars_start=1 + contributors_len + forks + 1
        stars_end= 1 + contributors_len + forks + 1 + stars_len

        G = nx.Graph()
        # labels = {}

        G.add_node(0)
        # labels[0] = 0

        for i in range(contributors_start, contributors_end):
                G.add_node(i)
                G.add_edge(0, i)
        #     labels[i] = i

        for i in range(forks_start, forks_end):
                G.add_node(i)
                G.add_edge(0, i)
        #     labels[i] = i

        for i in range(stars_start, stars_end):
                G.add_node(i)
                G.add_edge(0, i)
        #     labels[i] = i

        #partition = community.best_partition(G)  # compute communities
        pos = nx.spring_layout(G)

        nx.draw_networkx_nodes(G, pos,
                        nodelist=[0],
                        node_color='#FF99FF',
                        node_size=500,
                        alpha=1.0, label='Repository')

        nx.draw_networkx_nodes(G, pos,
                        nodelist=range(contributors_start, contributors_end),
                        node_color='#00FFCC',
                        node_size=100,
                        alpha=1.0, label='Contributors')

        nx.draw_networkx_nodes(G, pos,
                        nodelist=range(forks_start, forks_end),
                        node_color='#66CCFF',
                        node_size=100,
                        alpha=1.0, label='Forked')

        nx.draw_networkx_nodes(G, pos,
                        nodelist=range(stars_start,
                                        stars_end),
                        node_color='#FFFF00',
                        node_size=100,
                        alpha=1.0, label='Starred')

        contributors_edges = []
        for i in range(contributors_start, contributors_end):
                contributors_edges.append((0, i))

        forks_edges = []
        for i in range(forks_start, forks_end):
                forks_edges.append((0, i))

        stars_edges = []
        for i in range(stars_start, stars_end):
                stars_edges.append((0, i))

        nx.draw_networkx_edges(G, pos,
                        edgelist=contributors_edges,
                        width=1, alpha=0.8, edge_color='#9999FF')
        nx.draw_networkx_edges(G, pos,
                        edgelist=forks_edges,
                        width=1, alpha=0.8, edge_color='#9999FF')
        nx.draw_networkx_edges(G, pos,
                        edgelist=stars_edges,
                        width=1, alpha=0.8, edge_color='#9999FF')
        plt.title('Network Graph of '+ reponame + " Repository")
        plt.legend(loc='upper left', bbox_to_anchor=(1,1),labelspacing=1.5, borderpad=1)
        plt.tight_layout()
        plt.axis('off')
        # plt.axes()
        #plt.show()
        eachrepoimg = io.BytesIO()

        plt.savefig(eachrepoimg, format='png')
        eachrepoimg.seek(0)

        plot_url = base64.b64encode(eachrepoimg.getvalue()).decode()
        plt.clf()
        return'<img src="data:image2/png;base64,{}">'.format(plot_url)

if __name__ == '__main__':
   app.run(debug = True)
