# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_02_10_062838) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "interviews", force: :cascade do |t|
    t.string "channel_id"
    t.string "channel_name"
    t.datetime "created_at", null: false
    t.integer "duration", default: 0
    t.date "interview_date"
    t.string "interviewer"
    t.boolean "is_original", default: true
    t.bigint "parent_id"
    t.text "summary"
    t.string "thumbnail_url"
    t.string "title", null: false
    t.text "transcript"
    t.datetime "updated_at", null: false
    t.string "youtube_id", null: false
    t.string "youtube_url", null: false
    t.index ["interview_date"], name: "index_interviews_on_interview_date"
    t.index ["is_original"], name: "index_interviews_on_is_original"
    t.index ["parent_id"], name: "index_interviews_on_parent_id"
    t.index ["youtube_id"], name: "index_interviews_on_youtube_id", unique: true
  end

  add_foreign_key "interviews", "interviews", column: "parent_id"
end
