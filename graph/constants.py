# Constants:
NAMESPACE_ACTIVITY = 'activity:'
NAMESPACE_ENTITY = 'entity:'
NAMESPACE_COLUMN = 'column:'
NAMESPACE_TRACKER = 'tracker:'

# Neo4j CONSTANTS
ACTIVITY_LABEL = 'Activity'
ENTITY_LABEL = 'Entity'
COLUMN_LABEL = 'Column'
GENERATION_RELATION = 'WAS_GENERATED_BY'
USED_RELATION = 'USED'
DERIVATION_RELATION = 'WAS_DERIVED_FROM'
INVALIDATION_RELATION = 'WAS_INVALIDATED_BY'
NEXT_RELATION = 'NEXT'
BELONGS_RELATION = 'BELONGS_TO'
ACTIVITY_CONSTRAINT = 'constraint_activity_id'
ENTITY_CONSTRAINT = 'constraint_entity_id'
COLUMN_CONSTRAINT = 'constraint_column_id'

FUNCTION_EXECUTION_TIMES = 'function_execution_times.log'
NEO4j_QUERY_EXECUTION_TIMES = 'neo4j_query_execution_times.log'