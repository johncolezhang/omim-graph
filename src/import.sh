neo4j-admin import --database omim ^
  --nodes=phenotype_OMIM=import/pheno_omim.csv ^
  --nodes=HPO=import/hpo.csv ^
  --relationships=has_phenotype=import/omim_hpo_edge.csv ^
  --trim-strings=true ^
  --id-type=STRING