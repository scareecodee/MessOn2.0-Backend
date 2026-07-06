from sqlalchemy import (update,text,select,func)
from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.schemas.student.complaintSchema import ComplaintResponse,CreateComplaintRequest,ComplaintVoteRequest, ComplaintVoteResponse
from app.models.student.complaintModel import Complaints
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user.userModel import User
from app.models.student.complaintModel import Complaints
from app.models.student.complaintVoteModel import ComplaintVote
from app.utils.complaintVoteTypeEnum import ComplaintVoteTypeEnum

from sqlalchemy import  select,  tuple_
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.models.student.complaintModel import Complaints
from app.models.student.complaintVoteModel import ComplaintVote
from app.schemas.student.complaintSchema import ComplaintListResponse
from app.schemas.student.complaintFilterParams import  ComplaintFilterParams

from app.utils.complaintsPaginationCursor import (
    encode_complaint_cursor,
    decode_complaint_cursor
)

from app.utils.userRole import UserRole

async def create_complaint(
    db: AsyncSession,
    current_user: User,
    payload: CreateComplaintRequest
) -> None:

    student = await db.scalar(
        select(Student)
        .where(Student.user_id == current_user.id)
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    complaint = Complaints(
        id=uuid.uuid4(),
        user_id=current_user.id,
        college_id=current_user.college_id,
        mess_id=student.mess_id,
        subject=payload.subject.strip(),
        description=payload.description.strip(),
    )

    db.add(complaint)

    await db.commit()



async def set_complaint_vote_service(
    db: AsyncSession,
    current_user: User,
    payload: ComplaintVoteRequest
) -> ComplaintVoteResponse:

    # async with db.begin():

        complaint = await db.scalar(
            select(Complaints)
            .where(
                Complaints.id == payload.complaint_id
            )
            .with_for_update()
        )

        if complaint is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )

        existing_vote = await db.scalar(
            select(ComplaintVote)
            .where(
                ComplaintVote.complaint_id == payload.complaint_id,
                ComplaintVote.user_id == current_user.id
            )
        )

        if existing_vote is None:

            db.add(
                ComplaintVote(
                    complaint_id=payload.complaint_id,
                    user_id=current_user.id,
                    vote_type=payload.vote_type
                )
            )

            if payload.vote_type == ComplaintVoteTypeEnum.like:
                complaint.likes_count += 1
            else:
                complaint.dislikes_count += 1

            await db.commit()

            return ComplaintVoteResponse(
                likes_count=complaint.likes_count,
                dislikes_count=complaint.dislikes_count,
                user_vote=payload.vote_type
            )

       
        if (
            existing_vote.vote_type == ComplaintVoteTypeEnum.like
            and payload.vote_type == ComplaintVoteTypeEnum.like
        ):

            await db.delete(existing_vote)

            complaint.likes_count -= 1

            await db.commit()

            return ComplaintVoteResponse(
                likes_count=complaint.likes_count,
                dislikes_count=complaint.dislikes_count,
                user_vote=None
            )

       
        if (
            existing_vote.vote_type == ComplaintVoteTypeEnum.dislike
            and payload.vote_type == ComplaintVoteTypeEnum.dislike
        ):

            await db.delete(existing_vote)

            complaint.dislikes_count -= 1

            await db.commit()

            return ComplaintVoteResponse(
                likes_count=complaint.likes_count,
                dislikes_count=complaint.dislikes_count,
                user_vote=None
            )

        
        if (
            existing_vote.vote_type == ComplaintVoteTypeEnum.like
            and payload.vote_type == ComplaintVoteTypeEnum.dislike
        ):

            existing_vote.vote_type = ComplaintVoteTypeEnum.dislike

            complaint.likes_count -= 1
            complaint.dislikes_count += 1

            await db.commit()

            return ComplaintVoteResponse(
                likes_count=complaint.likes_count,
                dislikes_count=complaint.dislikes_count,
                user_vote=ComplaintVoteTypeEnum.dislike
            )

      
        existing_vote.vote_type = ComplaintVoteTypeEnum.like

        complaint.dislikes_count -= 1
        complaint.likes_count += 1

        await db.commit()

        return ComplaintVoteResponse(
            likes_count=complaint.likes_count,
            dislikes_count=complaint.dislikes_count,
            user_vote=ComplaintVoteTypeEnum.like
        )
    


async def fetch_complaints(
    db: AsyncSession,
    current_user: User,
    params: ComplaintFilterParams
) :

    VoteAlias = aliased(ComplaintVote)

    query = (
        select(
            Complaints,
            User,
            Student,
            VoteAlias.vote_type
        )
        .join(
            User,
            User.id == Complaints.user_id
        )
        .join(
            Student,
            Student.user_id == User.id
        )
    )

    #
    # Students need vote state
    #
    if current_user.role == UserRole.student:

        query = query.outerjoin(
            VoteAlias,
            (
                (VoteAlias.complaint_id == Complaints.id)
                &
                (VoteAlias.user_id == current_user.id)
            )
        )

    #
    # Admins don't vote
    #
    else:

        query = query.outerjoin(
            VoteAlias,
            VoteAlias.complaint_id == None
        )

    #
    # Status Filter
    #
    if params.status:

        query = query.where(
            Complaints.complaint_status ==
            params.status
        )

    #
    # Subject Search
    #
    if params.search:

        query = query.where(
            Complaints.subject.ilike(
                f"%{params.search.strip()}%"
            )
        )

    query = query.order_by(
        Complaints.created_at.desc(),
        Complaints.likes_count.desc(),
        Complaints.id.desc()
    )

    #
    # Cursor Pagination
    #
    if params.cursor:

        (
            cursor_created_at,
            cursor_likes,
            cursor_id
        ) = decode_complaint_cursor(
            params.cursor
        )

        query = query.where(
            tuple_(
                Complaints.created_at,
                Complaints.likes_count,
                Complaints.id
            )
            <
            (
                cursor_created_at,
                cursor_likes,
                cursor_id
            )
        )

    query = query.limit(
        params.limit + 1
    )

    result = await db.execute(query)

    rows = result.all()

    has_more = len(rows) > params.limit

    rows = rows[:params.limit]

    next_cursor = None

    if has_more:

        last_complaint = rows[-1][0]

        next_cursor = (
            encode_complaint_cursor(
                last_complaint.created_at,
                last_complaint.likes_count,
                last_complaint.id
            )
        )

    return ComplaintListResponse(
    complaints=[
        ComplaintResponse(
            complaint_id=complaint.id,
            student_name=user.name,
            student_roll_number=student.roll_number,
            subject=complaint.subject,
            description=complaint.description,
            likes_count=complaint.likes_count,
            dislikes_count=complaint.dislikes_count,
            complaint_status=complaint.complaint_status,
            created_at=complaint.created_at,
            user_vote=vote_type
        )
        for complaint, user, student, vote_type in rows
    ],
    next_cursor=next_cursor
)