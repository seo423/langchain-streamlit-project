import streamlit as st


def get_current_tool_message(tool_args, tool_call_id):
    """
    Get the tool message corresponding to the given tool call ID.

    Args:
        tool_args (list): List of tool arguments
        tool_call_id (str): ID of the tool call to find

    Returns:
        dict: Tool message if found, None otherwise
    """
    if tool_call_id:
        for tool_arg in tool_args:
            if tool_arg["tool_call_id"] == tool_call_id:
                return tool_arg
        return None
    else:
        return None


def format_search_result(results):
    """
    Format search results into a markdown string.

    Args:
        results (str): JSON string containing search results

    Returns:
        str: Formatted markdown string with search results
    """
    import json

    results = json.loads(results)

    answer = ""
    for result in results:
        answer += f'**[{result["title"]}]({result["url"]})**\n\n'
        answer += f'{result["content"]}\n\n'
        answer += f'신뢰도: {result["score"]}\n\n'
        answer += "\n-----\n"
    return answer


def stream_handler(streamlit_container, agent_executor, inputs, config):
    """
    Handle streaming of agent execution results in a Streamlit container.

    Args:
        streamlit_container (streamlit.container): Streamlit container to display results
        agent_executor: Agent executor instance
        inputs: Input data for the agent
        config: Configuration settings

    Returns:
        tuple: (container, tool_args, agent_answer)
            - container: Streamlit container with displayed results
            - tool_args: List of tool arguments used
            - agent_answer: Final answer from the agent
    """
    # Initialize result storage
    tool_args = [] # Agent가 사용한 도구 호출 정보를 저장하는 리스트
    agent_answer = ""
    agent_message = None  # Pre-declare agent_message variable

    container = streamlit_container.container()
    with container:
        for chunk_msg, metadata in agent_executor.stream(
            inputs, config, stream_mode="messages"
        ):
            # Agent가 Tool을 사용하려고 하면
            if hasattr(chunk_msg, "tool_calls") and chunk_msg.tool_calls:
                # Initialize tool call result
                tool_arg = {
                    "tool_name": "",
                    "tool_result": "",
                    "tool_call_id": chunk_msg.tool_calls[0]["id"],
                }
                # Save tool name
                tool_arg["tool_name"] = chunk_msg.tool_calls[0]["name"]
                if tool_arg["tool_name"]:
                    tool_args.append(tool_arg) # 도구 이름 저장

            # Tool을 호출할 때 전달하는 인자(arguments)가 streaming으로 들어오는 상황을 보는 코드
            # chunk_msg에 tool_call_chunks가 존재하고, 그 안에 뭔가 들어있다면,
            if hasattr(chunk_msg, "tool_call_chunks") and chunk_msg.tool_call_chunks:
                if len(chunk_msg.tool_call_chunks) > 0:  # Add None check
                    # Accumulate tool call arguments
                    # args에는 Agent가 Tool을 호출할 때 Tool에 전달하려는 입력값(인자)이 담김.
                    chunk_msg.tool_call_chunks[0]["args"] # 현재 메시지의 첫 번째 Tool 호출 조각에서 argument 부분만 가져옴
 
            # 실제 Tool이 실행되고 결과가 나오면 - 지금 들어온 메시지가 tools노드에서 나온건지 확인
            if metadata["langgraph_node"] == "tools":
                # Save tool execution results
                current_tool_message = get_current_tool_message(
                    tool_args, chunk_msg.tool_call_id
                )
                if current_tool_message:
                    # 검색결과 저장
                    current_tool_message["tool_result"] = chunk_msg.content
                    with st.status(f'✅ {current_tool_message["tool_name"]}'):
                        if current_tool_message["tool_name"] == "web_search":
                            # 만약 tool이 web search가 맞다면 검색 결과를 화면에 보여줌
                            st.markdown(
                                format_search_result(
                                    current_tool_message["tool_result"]
                                )
                            )

            # Agent가 최종 답변을 생성하면,
            # 메시지가 Agent가 직접 말하는 답변인지 확인
            if metadata["langgraph_node"] == "agent":
                if chunk_msg.content:
                    # Agent에서 온 답이 비어있지 않다면 st.empty()로 내용을 넣을 수 있는 빈공간 생성
                    if agent_message is None:
                        agent_message = st.empty()
                    # Accumulate agent message
                    agent_answer += chunk_msg.content
                    agent_message.markdown(agent_answer)

        # 최종답변과 검색한 결과를 보여주는 container반환, 도구 호출하면서 전달된 인자값, Agent답변
        return container, tool_args, agent_answer 