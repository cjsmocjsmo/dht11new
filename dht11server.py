import tornado.ioloop
import tornado.web
import tornado.options
import sqlite3
import json
from datetime import datetime

class CORSHandler(tornado.web.RequestHandler):
    """Base handler that adds CORS headers to all responses"""
    
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def options(self):
        # Handle preflight requests
        self.set_status(204)
        self.finish()

class HelloWorldHandler(CORSHandler):
    """Handler for the /helloworld endpoint"""
    
    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.write("Hello Fucker")

class CurrentTempHandler(CORSHandler):
    """Handler for the /current_temp endpoint"""
    
    def get(self):
        try:
            # Connect to the database
            conn = sqlite3.connect('/home/picam/dht11/dht11new/temperature_data.db')
            cursor = conn.cursor()
            
            # Get the most recent entry from the temps table
            cursor.execute('''
                SELECT C, F, humidity, time, date 
                FROM temps 
                ORDER BY id DESC 
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # Format the response as JSON
                response = {
                    "temperature_celsius": result[0],
                    "temperature_fahrenheit": result[1],
                    "humidity": result[2],
                    "time": result[3],
                    "date": result[4],
                    "timestamp": f"{result[4]} {result[3]}"
                }
                
                self.set_header("Content-Type", "application/json")
                self.write(json.dumps(response))
            else:
                # No data found
                self.set_status(404)
                self.set_header("Content-Type", "application/json")
                self.write(json.dumps({
                    "error": "No temperature data found",
                    "message": "The database appears to be empty or no readings have been taken yet."
                }))
                
        except sqlite3.Error as e:
            # Database error
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({
                "error": "Database error",
                "message": str(e)
            }))
            
        except Exception as e:
            # General error
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }))

class HealthHandler(CORSHandler):
    """Health check endpoint"""
    
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({
            "status": "healthy",
            "service": "DHT11 Temperature Server",
            "timestamp": datetime.now().isoformat()
        }))

def make_app():
    """Create and configure the Tornado application"""
    
    return tornado.web.Application([
        (r"/helloworld", HelloWorldHandler),
        (r"/current_temp", CurrentTempHandler),
        (r"/health", HealthHandler),
        (r"/", tornado.web.RedirectHandler, {"url": "/health"}),
    ], debug=True)

if __name__ == "__main__":
    # Configure command line options
    tornado.options.define("port", default=8888, help="run on the given port", type=int)
    tornado.options.define("host", default="0.0.0.0", help="bind to given address", type=str)
    tornado.options.parse_command_line()
    
    # Create the application
    app = make_app()
    
    # Start the server
    port = tornado.options.options.port
    host = tornado.options.options.host
    
    print(f"Starting DHT11 Temperature Server...")
    print(f"Server running on http://{host}:{port}")
    print(f"Endpoints:")
    print(f"  - GET /helloworld")
    print(f"  - GET /current_temp")
    print(f"  - GET /health")
    print("Press Ctrl+C to stop the server")
    
    app.listen(port, address=host)
    
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
