import subprocess

class DependencyChecker:
    def __init__(self):
        self.tools = {
            'ping': 'ping',
            'chromium': 'chromium',
            'firefox': 'firefox',
            # Añadir más según necesidad
        }

    def check_tool(self, tool):
        try:
            # Comando simple para verificar si está instalado (versión)
            result = subprocess.run([tool, '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, result.stdout.strip().split('\n')[0]
            else:
                return False, 'Error al ejecutar'
        except FileNotFoundError:
            return False, 'No instalado'
        except Exception as e:
            return False, f'Error: {str(e)}'

    def run_checks(self):
        status = {}
        for tool, cmd in self.tools.items():
            available, details = self.check_tool(cmd)
            status[tool] = {
                'available': available,
                'details': details
            }
        return status
