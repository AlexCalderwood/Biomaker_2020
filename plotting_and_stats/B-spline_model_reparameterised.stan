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

parameters {
  //start of my parameters
  
  // for group a
  real<lower=0> s_groups;
  //vector[num_groups] A_groups_raw[num_basis]; // stan can't do multiplication by scalars with 2d array(!)
  matrix[num_groups, num_basis] A_groups_raw;
  
  // for plant a
  real<lower=0> s_plants;
  matrix[num_plants, num_basis] A_plants_raw;
  
  // for observations
  real<lower=0> s_obs;
  
}

transformed parameters { // anything deterministic goes in transformed parameters rather than model
                         // stuff here has posteriors returned too! - nb yhat here!
  //vector[num_groups] A_groups[num_basis];
  matrix[num_groups, num_basis] A_groups;
  matrix[num_plants, num_basis] A_plants;
  matrix[num_plants, num_obs] Y_hat;
  
  // rescale A_groups from N(0,1) to N(0, s_groups). 
  A_groups = A_groups_raw * s_groups;
  
  // rescale A_plants from N(0,1) to N(A_groups[G[p], b], s_plants)
  for (p in 1:num_plants) {
    for (b in 1:num_basis) {
       A_plants[p, b] = (A_plants_raw[p, b] + A_groups[G[p], b]) * s_plants;
    }
  }
  
  Y_hat = A_plants * B;
  
  // TODO: use the differences in the A_group (between groups)
  // to estimate the differences between the groups at each timepoint. 
  // this can be used as the basis of statistical test for difference (does 95% CI 
  // for difference include 0?)
}

model {
  // a values for groups
  s_groups ~ cauchy(0, 1); // variability between groups
  
  for (g in 1:num_groups) {
    for (b in 1:num_basis) {
      A_groups_raw[g, b] ~ normal(0, 1);
    }
  }
  
  // a values for plants
  s_plants ~ cauchy(0, 1); // controls variability within a group
  
  for (p in 1:num_plants) {
    for (b in 1:num_basis) {
      //A_plants_raw[p, b] ~ normal(A_groups[G[p], b], 1); // drawn from normal with correct group mean for indiv. plant
      A_plants_raw[p, b] ~ normal(0, 1); // drawn from normal with correct group mean for indiv. plant
    }
  }
  
  // Y values
  s_obs ~ cauchy(0, 1);
  for (p in 1:num_plants) {
    for (o in 1:num_obs) {
      Y[p, o] ~ normal(Y_hat[p, o], s_obs);
    }
  }
}
