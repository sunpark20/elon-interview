class TimelineController < ApplicationController
  def index
    @interviews = Interview.originals.chronological

    if params[:year].present?
      @interviews = @interviews.by_year(params[:year].to_i)
    end

    if params[:interviewer].present?
      @interviews = @interviews.by_interviewer(params[:interviewer])
    end

    if params[:q].present?
      @interviews = @interviews.where("title ILIKE :q OR summary ILIKE :q OR interviewer ILIKE :q", q: "%#{params[:q]}%")
    end

    @grouped = @interviews.group_by(&:year)
    @years = Interview.originals.pluck(:interview_date).compact.map(&:year).uniq.sort.reverse
    @interviewers = Interview.originals.pluck(:interviewer).compact.uniq.sort
  end
end
