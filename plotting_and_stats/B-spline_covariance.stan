data {
  int num_plants; // the number of different plants
  int num_groups; // number of different plant groups (genotypes)
  int num_obs; // num datapoints per plant
  int num_basis; // num B-splines
  matrix[num_plants, num_obs] Y; // current trait observations
  vector[num_obs] X; 
  matrix[num_basis, num_obs] B; // values of the B-splines at the datapoint values of x.
  int G[num_plants]; // integer encoding of which group each plant's in. 
}

transformed data {
  int num_grp_sq = num_groups * num_groups; // used in generated quantities
}

parameters {
  //start of my parameters
  
  // for all
  row_vector[num_basis] a_all; // overall alphas (all plants derived from this)
  
  // for group
  corr_matrix[num_basis] Omega_g;
  vector<lower=0>[num_basis] tau_g;
  //row_vector[num_basis] A_groups[num_groups]; // 
  matrix[num_groups, num_basis] A_groups;
  
  // for plant a
  corr_matrix[num_basis] Omega_p;
  vector<lower=0>[num_basis] tau_p;
  //row_vector[num_basis] A_plants[num_plants]; // 
  matrix[num_plants, num_basis] A_plants;
  
  // for observations
  real<lower=0> s_obs;
  
}

transformed parameters { // anything deterministic goes in transformed parameters rather than model
                         // stuff here has posteriors returned too! - nb yhat here!
  //vector[num_groups] A_groups[num_basis];
  // matrix[num_groups, num_basis] A_groups;
  // matrix[num_plants, num_basis] A_plants; // needs to be matrix for dot product
  matrix[num_plants, num_obs] Y_hat; // ditto

  // // rescale A_groups from N(0,1) to N(0, 10).
  // for (g in 1:num_groups) {
  //   A_groups[g] = a_all + A_groups_raw[g] * 10; // worked well with 10, but ended up with correlated plants_raw and groups, try smaller group variation
  // }
  // 
  // // rescale A_plants from N(0,1) to N(A_groups[G[p], b], s_plants)
  // for (p in 1:num_plants) {
  //      A_plants[p] = (A_groups[G[p]]) + (A_plants_raw[p] * s_plants); // rewritten expanded which might help identifiability?? https://discourse.mc-stan.org/t/max-treedepth-warnings-in-hierarchical-multivariate-model/6514/8 jroon comment
  // }
  // 
  Y_hat = A_plants * B;
}

model {
  // root coefficients
  a_all ~ normal(0, 1);
  
  // a values for groups
  Omega_g ~ lkj_corr(2); // corr. matrix for a_group
  tau_g ~ normal(0, 1); // scaling for a_group
  for (g in 1:num_groups) {
    A_groups[g] ~ multi_normal(a_all, quad_form_diag(Omega_g, tau_g)); // draws a row at a time
  }

  // a values for plants
  Omega_p ~ lkj_corr(2); // corr. matrix for a_group
  tau_p ~ normal(0, 1); // scaling for a_group
  for (p in 1:num_plants) {
      A_plants[p] ~ multi_normal(A_groups[G[p]], quad_form_diag(Omega_p, tau_p)); // drawn from normal with correct group mean for indiv. plant
  }
  
  // Y values
  s_obs ~ cauchy(0, 1);
  for (p in 1:num_plants) {
      Y[p] ~ normal(Y_hat[p], s_obs); // indexing into matrix like this gets rows
  }
}

generated quantities {
  // Return the plant group level values, and the differences between
  // The groups
  
  //returned
  matrix[num_groups, num_obs] Y_group;
  matrix[num_grp_sq, num_obs] Y_diffs;
  
  //not returned
  {
    row_vector[num_basis] a_diff;
    int counter = 0;

    // group level observations
    Y_group = A_groups * B;
  
    // differences between groups
    for (i in 1:num_groups) {
      for (j in 1:num_groups) {
        counter += 1;
        a_diff = A_groups[i,:] - A_groups[j,:];
        Y_diffs[counter, :] = a_diff * B;
      }
    }
  }
}

