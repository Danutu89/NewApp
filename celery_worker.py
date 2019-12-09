from app import celery, db, app
from flask import session
from models import PostModel
import re
from analyze import parseVisitator, sessionID, GetSessionId, getAnalyticsData

@celery.task
def cleanup_sessions(*args, **kwargs):
    with app.test_client() as client:
        client.get('/flask_session')
        session.clear()


@celery.task
def verify_post(post_id, *args, **kwargs):
    post = db.session.query(PostModel).filter_by(id=post_id).first()
    bad_words = {}
    with open('banned_words.txt', encoding='utf8') as words:
        for l in words:
            bad_words[l.rstrip()] = len(l.rstrip()) * '*'

    substrings = sorted(bad_words, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    text = post.text
    result = regex.sub(lambda match: bad_words[match.group(0)], text)
    post.text = result
    db.session.commit()

@celery.task
def Parse_Visitator(data):
    parseVisitator(data)
