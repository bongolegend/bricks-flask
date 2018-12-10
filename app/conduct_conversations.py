from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from app.queries import query_user, query_last_exchange, insert_exchange, update_exchange
from app.routers import routers


RETRY = "Your response is not valid, try again.\n"


def main():
    """Respond to SMS inbound with appropriate SMS outbound based on last exchange"""
    inbound = request.values.get('Body')
    if inbound is None:
        return f"Please use a phone and text {os.environ.get('TWILIO_PHONE_NUMBER')}. This does not work thru the browser."

    user = query_user(request.values.get('From'))
    exchange = query_last_exchange(user)

    if exchange is None:
        router = routers['init_onboarding']()
    else:
        router = routers[exchange['router']]()

    parsed_inbound = router.parse(inbound)

    if parsed_inbound is not None:

        # give participation points
        points_message = router.insert_points(user)

        # execute current exchange actions after getting inbound
        # this needs to run before selecting the next router, as 
        # these actions can influence the next router choice
        action_results = router.run_actions(
            user=user,
            exchange=exchange,
            inbound=parsed_inbound)

        # decide on next router, including outbound and actions
        next_router = router.next_router(
            inbound=parsed_inbound,
            user=user)()
        
        # append last router's confirmation to next router's outbound
        if  router.confirmation is not None:
            next_router.outbound = router.confirmation + " " + next_router.outbound
        
        # prepend points message
        next_router.outbound = points_message + " " + next_router.outbound

    else:
        # resend the same router
        action_results = dict()
        next_router = router

        # prepend a string to the outbound saying you need to try again
        # this conditional is to prevent additional prepends on repeated failure 
        if RETRY not in exchange['outbound']:
            next_router.outbound = RETRY + next_router.outbound

    # run the pre-actions for next router before sending the outbound message
    pre_action_results = next_router.run_pre_actions(
        user=user,
        exchange=exchange)

    # combine all action results and add them to next router's outbound message
    results = {**action_results, **pre_action_results}
    next_router.outbound = next_router.outbound.format(**results) # TODO do I want to mutate this?

    # insert the next router into db as the next exchange
    next_exchange = insert_exchange(next_router, user)

    # update current exchange in DB with inbound and next exchange info
    update_exchange(exchange, next_exchange, parsed_inbound)

    # send outbound    
    resp = MessagingResponse()
    resp.message(next_exchange['outbound'])
    return str(resp)



