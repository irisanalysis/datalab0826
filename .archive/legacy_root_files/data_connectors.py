"""
Data connectors for various data sources
Simple mock implementation for testing
"""

import datetime

def test_data_source_connection(ds_type, config):
    """Test connection to data source"""
    try:
        # Simple validation - in real implementation would test actual connections
        if not config:
            return {
                "status": "failed", 
                "message": "Configuration is required"
            }
        
        # Mock successful connection for demonstration
        if ds_type in ['postgresql', 'mysql', 'mongodb']:
            required_fields = ['host', 'database', 'username']
            missing = [field for field in required_fields if not config.get(field)]
            if missing:
                return {
                    "status": "failed",
                    "message": f"Missing required fields: {', '.join(missing)}"
                }
        elif ds_type in ['csv', 'json']:
            if not config.get('file_path'):
                return {
                    "status": "failed",
                    "message": "File path is required"
                }
        elif ds_type == 'api':
            if not config.get('url'):
                return {
                    "status": "failed",
                    "message": "API URL is required"
                }
        
        # Mock successful connection
        return {
            "status": "connected",
            "message": f"Successfully connected to {ds_type} data source",
            "connection_time": 0.15,
            "server_version": "Mock v1.0"
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }

def get_connector(ds_type, config):
    """Get connector instance for data source type"""
    return MockConnector(ds_type, config)

class MockConnector:
    """Mock connector for demonstration"""
    
    def __init__(self, ds_type, config):
        self.ds_type = ds_type
        self.config = config
    
    def get_schema(self):
        """Get schema information"""
        try:
            # Mock schema based on data source type
            if self.ds_type in ['postgresql', 'mysql']:
                return {
                    "status": "success",
                    "schema": {
                        "databases": ["demo_db"],
                        "tables": [
                            {
                                "name": "users",
                                "columns": [
                                    {"name": "id", "type": "integer", "nullable": False},
                                    {"name": "email", "type": "varchar", "nullable": False},
                                    {"name": "created_at", "type": "timestamp", "nullable": False}
                                ]
                            },
                            {
                                "name": "orders", 
                                "columns": [
                                    {"name": "id", "type": "integer", "nullable": False},
                                    {"name": "user_id", "type": "integer", "nullable": False},
                                    {"name": "total", "type": "decimal", "nullable": False}
                                ]
                            }
                        ]
                    }
                }
            elif self.ds_type == 'mongodb':
                return {
                    "status": "success",
                    "schema": {
                        "databases": ["demo_db"],
                        "collections": [
                            {"name": "users", "document_count": 1250},
                            {"name": "products", "document_count": 543}
                        ]
                    }
                }
            elif self.ds_type in ['csv', 'json']:
                return {
                    "status": "success",
                    "schema": {
                        "columns": [
                            {"name": "id", "type": "number"},
                            {"name": "name", "type": "string"},
                            {"name": "value", "type": "number"}
                        ],
                        "row_count": 1000
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": f"Schema retrieval not implemented for {self.ds_type}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def query_data(self, query, limit=100):
        """Execute query and return data"""
        try:
            # Mock data based on data source type
            if self.ds_type in ['postgresql', 'mysql', 'mongodb']:
                # Mock query results
                mock_data = []
                for i in range(min(limit, 50)):  # Limit to 50 for demo
                    mock_data.append({
                        "id": i + 1,
                        "name": f"Record {i + 1}",
                        "value": round((i + 1) * 10.5, 2),
                        "created_at": (datetime.datetime.utcnow() - datetime.timedelta(days=i)).isoformat()
                    })
                
                return {
                    "status": "success",
                    "data": mock_data,
                    "columns": ["id", "name", "value", "created_at"],
                    "row_count": len(mock_data),
                    "execution_time": 0.023
                }
            elif self.ds_type in ['csv', 'json']:
                # Mock file data
                mock_data = []
                for i in range(min(limit, 25)):
                    mock_data.append({
                        "row_id": i + 1,
                        "category": f"Category {(i % 5) + 1}",
                        "amount": round((i + 1) * 15.75, 2)
                    })
                
                return {
                    "status": "success", 
                    "data": mock_data,
                    "columns": ["row_id", "category", "amount"],
                    "row_count": len(mock_data)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Query execution not implemented for {self.ds_type}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }