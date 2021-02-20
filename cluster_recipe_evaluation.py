import numpy as np
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


def compute_intra_cluster_dist(top_term_by_cluster_dict, glove_model):
  intra_cluster_dict = {}
  for cluster, term_tuple_list in top_term_by_cluster_dict.items():
    term_dict = {}
    intra_cluster_dict[cluster] = term_dict
    n_terms = sum([tup[1] for tup in term_tuple_list])
    for tup in term_tuple_list:
      term = tup[0]
      term_weight = tup[1]
      distance = 0
      for other_tup in term_tuple_list:
        other_term = other_tup[0]
        other_term_weight = other_tup[1]
        if term != other_term:
          distance +=  other_term_weight * glove_model.distance(term, other_term) 
      dist_mean = distance/(n_terms - term_weight)
      term_dict[term] = dist_mean
  return intra_cluster_dict

def compute_inter_cluster_distance(top_term_by_cluster_dict, glove_model):
  inter_cluster_dict = {}
  for cluster_1, term_tuple_list_1 in top_term_by_cluster_dict.items():
    term_dict = {}
    inter_cluster_dict[cluster_1] = term_dict
    for tup_1 in term_tuple_list_1:
      term = tup_1[0]
      term_dict[term] = []
      for cluster_2, term_tuple_list_2 in top_term_by_cluster_dict.items():
        if cluster_1 != cluster_2:
          distance = 0
          n_terms = sum([tup_2[1] for tup_2 in term_tuple_list_2])
          denom = n_terms
          for tup_2 in term_tuple_list_2:
            other_term = tup_2[0]
            other_term_weight = tup_2[1]
            if term != other_term:
              distance += glove_model.distance(term, other_term) * other_term_weight
            elif term == other_term:
              denom = denom - other_term_weight
          dist_mean = distance/denom
          term_dict[term].append(dist_mean)

  return {cluster: {term: min(dist_list) for term, dist_list in term_dist_dict.items()} for cluster,term_dist_dict in inter_cluster_dict.items()}

def compute_term_silhouette(inter_cluster_distance, intra_cluster_distance):
  d = {}
  for k1 in inter_cluster_distance.keys():
    d[k1] = {} 
    for k2 in inter_cluster_distance[k1].keys():
      inter = inter_cluster_distance[k1][k2]
      intra = intra_cluster_distance[k1][k2]
      if inter < 0 or intra < 0:
        print("WARNING: negative distance")
      silhouette = (inter - intra) / max(inter, intra)
      d[k1][k2] = silhouette
  return d

def compute_weighted_silhouette(clusters_terms_dict, silhouette_dict): 
  n_terms = sum([sum([tup[1] for tup in l]) for l in clusters_terms_dict.values()])
  sil_sum = 0
  for i in clusters_terms_dict.keys():
    sil_cluster_sum = 0
    for tup in clusters_terms_dict[i]:
      term = tup[0]
      weight = tup[1]
      sil_dist = silhouette_dict[i][term] * weight
      sil_cluster_sum += sil_dist
    sil_sum += sil_cluster_sum
  return sil_sum/n_terms