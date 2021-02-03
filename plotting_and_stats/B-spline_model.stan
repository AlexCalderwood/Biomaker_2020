data {
  int num_plants; // the number of different plants
  int num_groups; // number of different plant groups (genotypes)
  int num_obs; // num datapoints per plant
  int num_basis; // num B-splines
  int G[num_plants]; // coding which group membership of plants 
  vector[num_obs] X; // x-axis in arbitrary units
  matrix[num_plants, num_obs] Y; // trait observations
  matrix[num_basis, num_obs] B; // B-spline function values
}

transformed data {
  int num_grp_comparisons = (num_groups * (num_groups - 1)) / 2; // number of pairwise comparisons between groups
}

parameters {
  // for all
  //row_vector[num_basis] a_all; // overall alphas (all plants derived from this). Inclusion in model makes slower
  
  // for group
  real<lower=0> s_group; // assume all group a have same st. dev., and all independent.
  row_vector[num_basis] A_groups_raw[num_groups];
  
  // for plant 
  real<lower=0> s_plants; // assumes all plant a have same st. dev., and all independent.
  row_vector[num_basis] A_plants_raw[num_plants];
  
  // for observations
  real<lower=0> s_obs;
  
}

transformed parameters { 
  // need to be matrix for dot products
  matrix[num_groups, num_basis] A_groups;
  matrix[num_plants, num_basis] A_plants; 
  matrix[num_plants, num_obs] Y_hat;
  
  // non-centered paramaterisations avoid divergence (avoid Neal's funnel effect)
  // rescale A_groups from N(0,1) to N(0, s_group).
  for (g in 1:num_groups) {
    A_groups[g] = A_groups_raw[g] * s_group; // worked well with 10, but ended up with correlated plants_raw and groups, try smaller group variation
  }
  
  // rescale A_plants from N(0,1) to N(A_groups[G[p], b], s_plants)
  for (p in 1:num_plants) {
       A_plants[p] = (A_groups[G[p]]) + (A_plants_raw[p] * s_plants); // rewritten expanded which might help identifiability?? https://discourse.mc-stan.org/t/max-treedepth-warnings-in-hierarchical-multivariate-model/6514/8 jroon comment
  }
  
  Y_hat = A_plants * B;
}

model {
  // all level
  // a_all ~ normal(0, 1); // turns out slower with common a level (and no better fit - loads of data, so think data sharing not so important!)
  
  // groups level
  s_group ~ cauchy(0, 1);
  for (g in 1:num_groups) {
    A_groups_raw[g] ~ normal(0, 1); // vectorised, draws a row at a time (no way to draw full matrix at once).
  }

  // plants level
  s_plants ~ cauchy(0, 1); 
  for (p in 1:num_plants) {
      A_plants_raw[p] ~ normal(0, 1);
  }
  
  // observed Y values
  s_obs ~ cauchy(0, 1);
  for (p in 1:num_plants) {
      Y[p] ~ normal(Y_hat[p], s_obs);
  }
}

generated quantities {
  // Return the plant group level Y values, and the differences between
  // the groups
  
  // returned variables
  matrix[num_groups, num_obs] Y_group; // group level Y-values
  matrix[num_grp_comparisons, num_obs] Y_diffs; // differences between group Y-values
  
  // not returned variables
  {
    int row_counter = 0;

    // group level observations
    Y_group = A_groups * B;
  
    // differences between groups
    for (i in 1:num_groups) {
      for (j in 1:num_groups) {
        if (i < j) {
          row_counter += 1;
          Y_diffs[row_counter] = Y_group[i] - Y_group[j];
        }
      }
    }
    
  }
}
