neo4j-admin import --database omim ^
  --nodes=csv_upload/pheno_omim.csv ^
  --nodes=csv_upload/hpo.csv ^
  --nodes=csv_upload/variant_location.csv ^
  --nodes=csv_upload/rsID_merge.csv ^
  --nodes=csv_upload/pubmed.csv ^
  --nodes=csv_upload/gene_merge.csv ^
  --nodes=csv_upload/clean_drug_graph.nodes.chemical.csv ^
  --nodes=csv_upload/clean_drug_graph.nodes.diplotype.csv ^
  --nodes=csv_upload/clean_drug_graph.nodes.disease.csv ^
  --nodes=csv_upload/clean_drug_graph.nodes.drug.csv ^
  --nodes=csv_upload/clean_drug_graph.nodes.nmpa_drug.csv ^
  --nodes=csv_upload/clean_drug_graph.nodes.symptom.csv ^
  --nodes=csv_upload/clean_drug_graph.nodes.variant.haplotype.csv ^
  --relationships=csv_upload/omim_hpo_edge.csv ^
  --relationships=csv_upload/omim_location_edge.csv ^
  --relationships=csv_upload/hpo_location_edge.csv ^
  --relationships=csv_upload/location_rsID_edge.csv ^
  --relationships=csv_upload/pubmed_gene_edge.csv ^
  --relationships=csv_upload/pubmed_rsid_edge.csv ^
  --relationships=csv_upload/omim_gene_edge.csv ^
  --relationships=csv_upload/hpo_gene_edge.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.chemical_drug_relation.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.clinical_annotation.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.cn_drug_label.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.cpic_guideline.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.diplotype_consist_of.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.diplotype_metabolizer.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.drug_consist_of.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.drug_label.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.guideline_annotation.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.haplotype_rsID_related.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.has_symptom.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.mutation_at.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.research_annotation.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.treatment.csv ^
  --relationships=csv_upload/clean_drug_graph.relationships.variant_guideline.csv ^
  --trim-strings=true ^
  --id-type=STRING ^
  --skip-duplicate-nodes=true ^
  --skip-bad-relationships=true ^
  --input-encoding=utf-8 ^
  --multiline-fields=true


neo4j-admin dump --database=omim --to=d:/neo4j_dump/omim.db.2022_05_07.dump

neo4j-admin load --from=<file_path> --database=neo4j --force
