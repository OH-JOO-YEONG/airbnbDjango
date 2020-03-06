from django import template

register = template.Library()

@register.filter # filter뒤에 ()가 없을 때는 sexy_capitals라는 함수를 로드해야한다.  함수의 이름을 마음대로 바꿔도 register.filter(name="sexy_capitals") 로 바꿔주면 역시 실행된다.
def sexy_capitals(value):
    print(value)
    return "lalalala"