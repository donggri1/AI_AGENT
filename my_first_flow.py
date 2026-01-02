from crewai.flow.flow import Flow, listen,start,router,and_,or_
from pydantic import BaseModel

class MyFirstFlowState(BaseModel):
    hello : str = ""


class MyFirstFlow(Flow[MyFirstFlowState]):

    @start()
    def start_flow(self):
        self.state.hello = "hello"
        print("hello start")
        return 123

    @listen(start_flow)
    def first_step(self, num):
        self.state.hello = "world"
        print("hello first step")
        print(f"num : {num}")

    @listen(first_step)
    def second_step(self):
        print(f"hello state : {self.state.hello}")

    @listen(and_(first_step, second_step))
    def and_dummy_func(self):
        print("and dummy function")

    @listen(or_(first_step, second_step))
    def or_dummy_func(self):
        print("or dummy function")
    # 라우터는 반드시 리스너 다음에 와야함 그리고 리턴값이 있어야하며 그 리턴값이 다음 리스너의 인자가 됨
    @router(second_step)
    def router_to_end(self):
        print("router to end")
        check = True

        if check:
            return "check is true"
        else:
            return "check is false"

    @listen("check is true")
    def end_flow(self):
        print("end flow")

flow = MyFirstFlow()
flow.kickoff()
