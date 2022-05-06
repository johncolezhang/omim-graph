neo4j-admin import --database omim ^
  --nodes=phenotype_OMIM=import/pheno_omim.csv ^
  --nodes=HPO=import/hpo.csv ^
  --nodes=variant_location=import/variant_location.csv ^
  --nodes=rsID:variant=import/rsID.csv ^
  --nodes=pubmed=import/pubmed.csv ^
  --nodes=gene=import/gene.csv ^
  --relationships=has_phenotype=import/omim_hpo_edge.csv ^
  --relationships=clinvar_variant_omim_relation=import/omim_location_edge.csv ^
  --relationships=clinvar_variant_hpo_relation=import/hpo_location_edge.csv ^
  --relationships=rsID_location_mapping=import/location_rsID_edge.csv ^
  --relationships=research_in_gene=import/pubmed_gene_edge.csv ^
  --relationships=research_in_rsID=import/pubmed_rsid_edge.csv ^
  --relationships=omim_gene_influence=import/omim_gene_edge.csv ^
  --relationships=hpo_gene_influence=import/hpo_gene_edge.csv ^
  --trim-strings=true ^
  --id-type=STRING ^
  --skip-duplicate-nodes=true ^
  --skip-bad-relationships=true


neo4j-admin dump --database=omim --to=d:/neo4j_dump/omim.db.2022_05_06.dump
