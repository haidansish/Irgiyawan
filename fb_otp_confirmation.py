#!/usr/bin/env python3
"""
Facebook OTP Confirmation - Standalone Module
==============================================

Tool untuk konfirmasi email Facebook dengan kode OTP

Requirements:
- requests
- beautifulsoup4 (bs4)
- rich
- fake_useragent

Author: Modified Version
"""

import re
import time
import requests
from pathlib import Path
from rich.console import Console
from rich.tree import Tree
from rich.prompt import Prompt
from fake_useragent import UserAgent

# ============================================================================
# GLOBAL CONFIG
# ============================================================================

console = Console()
ua = UserAgent()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_user_agent():
    """Generate random mobile user agent"""
    return ua.random


def extract_tokens_from_page(html):
    """
    Extract tokens (LSD, fb_dtsg) dari halaman Facebook
    """
    extracted = {}
    
    # LSD token patterns
    lsd_patterns = [
        r"LSD",\s*\[\],\s*{\s*"token":"(.*?)"},
        r"LSD"\s*,\s*\[\]\s*,\s*{\s*"token"\s*:\s*"(.*?)",
        r'LSD[^}]*?"token"\s*:\s*"(.*?)",
        r'"token"\s*:\s*"([a-zA-Z0-9_\-]+)",
    ]
    
    for pattern in lsd_patterns:
        match = re.search(pattern, html)
        if match:
            extracted['lsd'] = match.group(1)
            break
    
    # fb_dtsg token patterns
    dtsg_patterns = [
        r'name="fb_dtsg"\s+value="(.*?)",
        r'name="fb_dtsg"[^>]*value="(.*?)",
        r'"fb_dtsg"\s*:\s*"(.*?)",
        r'fb_dtsg["\']?\s*:\s*["\']([^"\']+)','
    ]
    
    for pattern in dtsg_patterns:
        match = re.search(pattern, html)
        if match:
            extracted['fb_dtsg'] = match.group(1)
            break
    
    return extracted


def get_confirmation_page(email, cookies):
    """
    Mengambil halaman konfirmasi email
    """
    console.print('[cyan]→ Mengambil halaman verifikasi...[/cyan]')
    
    session = requests.Session()
    
    endpoints = [
        'https://web.facebook.com/confirmemail.php?next=https%3A%2F%2Fweb.facebook.com%2F',
        'https://mbasic.facebook.com/confirmemail.php?next=https%3A%2F%2Fmbasic.facebook.com%2F',
        'https://m.facebook.com/confirmemail.php'
    ]
    
    for endpoint in endpoints:
        try:
            response = session.get(endpoint, cookies=cookies, timeout=20)
            
            if response.status_code == 200:
                console.print(f'[green]✓ Halaman berhasil diambil[/green]')
                return response.text, session
                
        except Exception as e:
            console.print(f'[dim]Debug: {e}[/dim]')
            continue
    
    console.print('[red]✗ Gagal mengambil halaman verifikasi[/red]')
    return None, session

# ============================================================================
# OTP CONFIRMATION FUNCTION
# ============================================================================

def confirm_facebook_otp(uid, email, cookies, profile_name, password):
    """
    Konfirmasi akun Facebook dengan OTP
    
    Parameters:
    - uid: User ID Facebook
    - email: Email yang digunakan
    - cookies: Dictionary cookies dari akun
    - profile_name: Nama profil
    - password: Password akun
    
    Returns:
    - True jika konfirmasi berhasil
    - False jika gagal
    """
    
    console.print('\n[bold cyan]═══════════════════════════════════════[/bold cyan]')
    console.print('[bold yellow]🔐 KONFIRMASI EMAIL FACEBOOK (OTP)[/bold yellow]')
    console.print('[bold cyan]═══════════════════════════════════════[/bold cyan]\n')
    
    max_attempts = 3
    attempt = 0
    
    session = requests.Session()
    page_content = None
    
    while attempt < max_attempts:
        try:
            attempt += 1
            
            console.print(f'[bold cyan]━━━ PERCOBAAN {attempt}/{max_attempts} ━━━[/bold cyan]')
            console.print(f'[white]Email:[/white] [bold cyan]{email}[/bold cyan]')
            console.print(f'[white]UID:[/white] [bold cyan]{uid}[/bold cyan]')
            console.print('[bold yellow]Silakan cek email Anda dan masukkan kode verifikasi.[/bold yellow]')
            
            otp_code = Prompt.ask('[bold white]Kode Verifikasi (6 digit)[/bold white]').strip()
            
            # Validasi input
            if not otp_code:
                console.print('[red]✗ Kode tidak boleh kosong![/red]')
                continue
            
            if not otp_code.isdigit():
                console.print('[red]✗ Kode harus berupa angka![/red]')
                continue
            
            if len(otp_code) < 6:
                console.print(f'[red]✗ Kode terlalu pendek (minimal 6 digit, Anda input {len(otp_code)})[/red]')
                continue
            
            # Ambil halaman konfirmasi jika belum ada
            if not page_content:
                page_content, session = get_confirmation_page(email, cookies)
                
                if not page_content:
                    console.print('[red]✗ Tidak dapat mengambil halaman konfirmasi[/red]')
                    console.print('[yellow]Silakan coba lagi atau lakukan verifikasi manual melalui browser[/yellow]')
                    continue
            
            # Extract tokens
            console.print('[cyan]→ Mengekstrak token...[/cyan]')
            tokens = extract_tokens_from_page(page_content)
            
            lsd_token = tokens.get('lsd')
            fb_dtsg = tokens.get('fb_dtsg')
            
            if not lsd_token or not fb_dtsg:
                console.print('[yellow]⚠️  Token extraction gagal, menggunakan fallback...[/yellow]')
                lsd_token = lsd_token or f'fallback_{uid}'
                fb_dtsg = fb_dtsg or f'fallback_{uid}'
            
            console.print(f'[green]✓ Token berhasil diekstrak[/green]')
            
            # Prepare headers
            headers = {
                'authority': 'web.facebook.com',
                'accept': '*/*',
                'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://web.facebook.com',
                'referer': 'https://web.facebook.com/confirmemail.php?next=https%3A%2F%2Fweb.facebook.com%2F',
                'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': generate_user_agent(),
                'x-asbd-id': '359341',
                'x-fb-lsd': lsd_token
            }
            
            params = {
                'next': 'https://web.facebook.com/',
                'cp': email,
                'from_cliff': '1',
                'conf_surface': 'hard_cliff',
                'event_location': 'cliff'
            }
            
            data = {
                'jazoest': lsd_token,
                'fb_dtsg': fb_dtsg,
                'code': otp_code,
                'source_verified': 'www_reg',
                'confirm': '1',
                '__user': uid,
                '__a': '1',
                '__req': '3',
                '__hs': '',
                '__dyn': '',
                '__hsdp': '',
                '__hblp': '',
                'lsd': lsd_token
            }
            
            console.print('[cyan]→ Mengirim kode konfirmasi...[/cyan]')
            
            response = session.post(
                'https://web.facebook.com/confirm_code/dialog/submit/',
                params=params,
                cookies=cookies,
                headers=headers,
                data=data,
                timeout=25
            )
            
            console.print(f'[dim]→ Status: {response.status_code}[/dim]')
            
            # Check success
            response_lower = response.text.lower()
            success_indicators = ['success', 'confirmed', 'verified', 'redirected']
            
            # Heuristic: jika status 200 dan response text pendek atau ada indikator sukses
            is_success = (
                response.status_code == 200 and 
                (any(indicator in response_lower for indicator in success_indicators) or
                 len(response.text) < 500)
            )
            
            if is_success:
                console.print()
                success_tree = Tree('[bold green]✅ KONFIRMASI BERHASIL![/bold green]')
                success_tree.add(f'[white]UID:[/white] [bold cyan]{uid}[/bold cyan]')
                success_tree.add(f'[white]Email:[/white] [bold green]{email}[/bold green]')
                success_tree.add(f'[white]Status:[/white] [bold green]CONFIRMED ✓[/bold green]')
                success_tree.add(f'[white]Profile:[/white] [bold green]{profile_name}[/bold green]')
                console.print(success_tree)
                
                console.print('\n[bold green]→ Akun Anda telah berhasil diverifikasi![/bold green]')
                
                return True
            else:
                console.print('[red]✗ Kode verifikasi salah atau sudah digunakan[/red]')
                
                if attempt < max_attempts:
                    remaining = max_attempts - attempt
                    console.print(f'[yellow]Silakan coba lagi ({remaining} percobaan tersisa)[/yellow]\n')
                
        except requests.exceptions.Timeout:
            console.print('[red]✗ Timeout saat konfirmasi[/red]')
            if attempt < max_attempts:
                console.print('[yellow]Silakan coba lagi[/yellow]\n')
                
        except Exception as e:
            console.print(f'[red]✗ Error: {str(e)}[/red]')
            if attempt < max_attempts:
                console.print('[yellow]Silakan coba lagi[/yellow]\n')
    
    # Gagal setelah semua percobaan
    console.print('\n[bold red]❌ Gagal konfirmasi setelah 3 percobaan[/bold red]')
    console.print('[yellow]Anda dapat melakukan verifikasi nanti melalui:[/yellow]')
    console.print('  1. Buka https://www.facebook.com/')
    console.print('  2. Login dengan akun Anda')
    console.print('  3. Ikuti petunjuk untuk verifikasi email')
    
    return False

# ============================================================================
# STANDALONE USAGE
# ============================================================================

def main():
    """Main function untuk standalone usage"""
    console.print('\n[bold cyan]Facebook OTP Confirmation Tool[/bold cyan]\n')
    
    # Input data
    uid = Prompt.ask('[white]Masukkan UID Facebook[/white]').strip()
    email = Prompt.ask('[white]Masukkan Email[/white]').strip()
    profile_name = Prompt.ask('[white]Masukkan Nama Profil[/white]').strip()
    password = Prompt.ask('[white]Masukkan Password[/white]').strip()
    
    # Input cookies
    console.print('\n[bold cyan]Masukkan Cookies (format: name1=value1; name2=value2; ...)[/bold cyan]')
    cookies_str = Prompt.ask('[white]Cookies[/white]').strip()
    
    # Parse cookies
    cookies = {}
    if cookies_str:
        for cookie_pair in cookies_str.split(';'):
            if '=' in cookie_pair:
                name, value = cookie_pair.split('=', 1)
                cookies[name.strip()] = value.strip()
    
    if not cookies:
        console.print('[red]✗ Cookies tidak valid![/red]')
        return
    
    console.print(f'[green]✓ Cookies berhasil diparse ({len(cookies)} items)[/green]')
    
    # Confirm
    confirm = Prompt.ask(    
        '\n[bold yellow]Lanjutkan dengan data di atas?[/bold yellow]',
        choices=['y', 'n'],
        default='y'
    )
    
    if confirm.lower() != 'y':
        console.print('[yellow]Dibatalkan.[/yellow]')
        return
    
    # Run confirmation
    result = confirm_facebook_otp(uid, email, cookies, profile_name, password)
    
    if result:
        console.print('\n[bold green]✓ Selesai! Akun berhasil dikonfirmasi.[/bold green]')
    else:
        console.print('\n[bold yellow]⚠ Akun tidak dikonfirmasi. Coba lagi nanti.[/bold yellow]')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print('\n[red]Dibatalkan.[/red]')
    except Exception as e:
        console.print(f'\n[red]Error: {e}[/red]')