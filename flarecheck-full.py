import requests
from dns import resolver
import ipaddress

def get_cloudflare_ip_ranges():
    response = requests.get("https://www.cloudflare.com/ips-v4")
    response.raise_for_status()
    return response.text.strip().split('\n')

def is_cloudflare_ip(ip, ranges):
    for ip_range in ranges:
        if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(ip_range):
            return True
    return False

def check_cloudflare(domains):
    results = {}
    cf_ip_ranges = get_cloudflare_ip_ranges()
    for domain in domains:
        domain = domain.strip()
        try:
            response = requests.get(f"http://{domain}", timeout=5)
            is_cf = "cloudflare" in response.headers.get('Server', '').lower()
            
            answers = resolver.resolve(domain, 'A')
            ip_addresses = [answer.to_text() for answer in answers]
            is_cf_ip = any(is_cloudflare_ip(ip, cf_ip_ranges) for ip in ip_addresses)
            
            if is_cf or is_cf_ip:
                results[domain] = True
        except (requests.exceptions.RequestException, resolver.NXDOMAIN, resolver.NoAnswer, resolver.NoNameservers):
            results[domain] = "Error"
    return results

def save_to_html(results):
    with open('results.html', 'w') as f:
        f.write('<html><body>')
        f.write('<div style="text-align:center;"><img src="logo.png" alt="Logo"></div>')
        f.write('<table border="1" style="margin: 0 auto;">')
        f.write('<tr><th>Domain</th><th>On Cloudflare</th></tr>')
        for domain, is_on_cloudflare in results.items():
            if is_on_cloudflare == True:
                f.write(f'<tr><td>{domain}</td><td>{is_on_cloudflare}</td></tr>')
        f.write('</table></body></html>')

# Read domains from a text file and store them in a list
with open('domains.txt', 'r') as f:
    domains = f.readlines()

# Usage:
results = check_cloudflare(domains)
save_to_html(results)
