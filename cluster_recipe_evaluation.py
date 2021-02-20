from collections import Counter

def prepare_cluster_recipe_list(recipe_list, stopword_list):
  recipe_list = [x.lower() for x in recipe_list]
  recipe_list = [word for line in recipe_list for word in line.split(sep=" ") if word not in stopword_list]
  return recipe_list

def select_top_n_terms(recipe_list, n):
  counted_terms = Counter(recipe_list)
  most_common_terms = [tup for tup in counted_terms.most_common(n)]
  return most_common_terms

def select_top_perc_terms(recipe_list, percentage):
  total_terms = len(recipe_list)
  counted_terms = Counter(recipe_list).most_common()

  cumulative_perc = np.cumsum([tup[1] for tup in counted_terms])/total_terms
  terms = [tup[0] for tup in counted_terms]
  relative_freq_terms = list(zip(terms, cumulative_perc, counted_terms))
  filtered_terms = list(filter(lambda x: x[1] <= percentage, relative_freq_terms))
  
  return [tup[2] for tup in filtered_terms]

def create_clusters_terms_dict(cluster_df, stopword_list, percentage):
  full_clusters_terms_dict = cluster_df.groupby('cluster')['recipe_name'].apply(list)
  full_clusters_terms_dict = full_clusters_terms_dict.to_dict()
  clean_clusters_terms_dict = {k: prepare_cluster_recipe_list(v, stopword_list) for k, v in full_clusters_terms_dict.items()}
  top_clusters_terms_dict = {k: select_top_perc_terms(v, percentage) for k, v in clean_clusters_terms_dict.items()}
  return top_clusters_terms_dict
