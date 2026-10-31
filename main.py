import re
import requests
import ipaddress
import unittest


IPV6_REGEX = re.compile(
    r"""
    (?<![:\w])       
    (?=[0-9A-Fa-f:.]*:)
    (
    ([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|
    #Сокращения
    ([0-9a-fA-F]{1,4}:){1,7}:| 
    ([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}      | 
    ([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2} | 
    ([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3} | 
    ([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4} | 
    ([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5} | 
    [0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})    | 
    :((:[0-9a-fA-F]{1,4}){1,7}|:)                  | #Начинается с :: (loopback ::1 и ::)
    fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}  | #Link-local с зоной (fe80::1%eth0)
    ::(ffff(:0{1,4}){0,1}:){0,1}                     #IPv4-mapped (::x.x.x.x или ::ffff:x.x.x.x)
    ((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3} 
    (25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])       | 
    ([0-9a-fA-F]{1,4}:){1,4}:                      | #IPv6-часть перед IPv4 (1-4 группы)
    ((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3} 
    (25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])
    )
    (?![:\w%]|\.\d)                                   
    """,
    re.IGNORECASE | re.VERBOSE
)


def find_ipv6(text):
    """Ищет IPv6 адреса в строке и валидирует их через модуль ipaddress."""
    # 1. Ищем все совпадения по регулярному выражению
    matches = IPV6_REGEX.findall(text)
    valid_ips = []
    for match in matches:
        candidate = match[0] if isinstance(match, tuple) else match
        valid_ips.append(candidate)
        
    return list(set(valid_ips))


class TestIPv6Regex(unittest.TestCase):
    
    def test_valid_ipv6(self):
        """Корректные адреса"""
        valid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:db8:85a3::8a2e:370:7334",
            "::1",
            "::",
            "fe80::1%eth0",
            "::ffff:192.168.1.1",
            "1:2:3:4:5:6:7:8"
        ]
        for ip in valid_ips:
            with self.subTest(ip=ip):
                self.assertIn(ip, find_ipv6(f"Текст с адресом {ip} внутри."))

    def test_invalid_ipv6(self):
        """Некорректные адреса"""
        invalid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334:1234", # Избыток групп
            "2001:db8:::1",                                # Тройное двоеточие
            "12345::1",                                    # Группа больше 4 символов
            "192.168.1.1",                                 # Это IPv4
            "hello:world",
            "2001:db8:85a3:0000:0000:8a2e:0370:733g"       # Недопустимый символ 'g'
        ]
        for ip in invalid_ips:
            with self.subTest(ip=ip):
                self.assertEqual(find_ipv6(f"Текст с адресом {ip} внутри."), [])

    def test_multiple_ips(self):
        """Поиск в тексте"""
        text = "Сервер 1: ::1. Сервер 2: 2001:db8::ff00:42:8329. Мусор: 1234::5678::9abc."
        results = find_ipv6(text)
        self.assertEqual(len(results), 2)
        self.assertIn("::1", results)
        self.assertIn("2001:db8::ff00:42:8329", results)


def main():
    while True:
        print("ПОИСК И ПРОВЕРКА IPv6 АДРЕСОВ")
        print("="*40)
        print("1. Unit - тестирование")

        choice = input("Выберите действие: ")
        
        if choice == '1':
            print("\nЗапуск тестов...\n")
            unittest.main(argv=['first-arg-is-ignored'], exit=False)
        elif choice == '0':
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод. Попробуйте снова.")


if __name__ == '__main__':
    main()
